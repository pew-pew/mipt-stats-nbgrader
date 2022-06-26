c = get_config()

c.ClearSolutions.begin_solution_delimeter = "BEGIN SOLUTION"
c.ClearSolutions.end_solution_delimeter = "END SOLUTION"
c.ClearSolutions.code_stub = {
    "python": "... # Ваше решение тут",
}

## The time to wait (in seconds) for output from executions. If a cell execution
#  takes longer, a TimeoutError is raised.
#  
#  ``None`` or ``-1`` will disable the timeout. If ``timeout_func`` is set, it
#  overrides ``timeout``.
#  Default: None
c.NotebookClient.timeout = 800
# TODO: doesn't work, see https://github.com/jupyter/nbgrader/issues/1463
