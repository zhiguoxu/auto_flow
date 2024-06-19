from __future__ import annotations

import threading
import uuid
from contextvars import ContextVar
from typing import Dict, Any, List

from pydantic import BaseModel, Field

from core.flow.flow import Flow


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flow: Flow
    config: Dict[str, Any]
    input: Any
    output: Any = None
    error: BaseException | None = None
    thread_id: int = Field(default_factory=threading.get_ident)

    class Config:
        arbitrary_types_allowed = True


class RunStack(BaseModel):
    stack: List[Run] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.stack) == 0

    def push(self, run: Run) -> None:
        self.stack.append(run)

    def pop(self) -> Run:
        if not self.is_empty():
            return self.stack.pop()
        raise IndexError("pop from empty stack")

    def peek(self) -> Run:
        if not self.is_empty():
            return self.stack[-1]
        raise IndexError("peek from empty stack")

    def size(self) -> int:
        return len(self.stack)


var_run_stack = ContextVar("var_run_stack", default=RunStack())


def push_run_stack(run: Run) -> None:
    run_stack = var_run_stack.get()
    if run_stack.is_empty():
        run_stack.push(run)
    else:
        assert run_stack.peek().flow.id != run.flow.id, \
            f"Flow has re-enter the stack, maybe you have trace one flow more than once: {run.flow}"
        parent_thread_id = run_stack.peek().thread_id
        if parent_thread_id == run.thread_id:
            run_stack.push(run)
        else:
            run_stack = RunStack(stack=run_stack.stack)  # Copy stack in new thread for parallel.
            run_stack.push(run)
            var_run_stack.set(run_stack)


def pop_run_stack() -> Run:
    return var_run_stack.get().pop()


def current_run_list() -> List[Run]:
    return var_run_stack.get().stack


def current_run() -> Run:
    return var_run_stack.get().peek()


def current_flow() -> Flow:
    return current_run().flow


def is_run_stack_empty():
    return var_run_stack.get().is_empty()