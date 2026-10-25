from tpd_spectra.gui import workflow_guidance


def test_empty_workspace_prompts_import():
    assert "Import CSV" in workflow_guidance(0, 0)


def test_hidden_traces_have_recovery_instruction():
    message = workflow_guidance(3, 0)
    assert "Show all" in message


def test_imported_and_visible_counts_are_clear():
    message = workflow_guidance(5, 2)
    assert "2 visible of 5 imported" in message
    assert "Run full analysis" in message


def test_running_state_does_not_prompt_another_run():
    message = workflow_guidance(3, 3, running=True)
    assert "Analyzing" in message
    assert "select Run" not in message
