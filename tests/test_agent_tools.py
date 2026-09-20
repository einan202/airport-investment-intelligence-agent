from agent.tools import tools


def test_regional_expansion_tool_is_exposed():
    tool_names = {
        tool["function"]["name"]
        for tool in tools
    }

    assert "rank_regional_expansion_candidates" in tool_names


def test_validator_is_not_exposed_as_separate_agent_tool():
    tool_names = {
        tool["function"]["name"]
        for tool in tools
    }

    assert "validate_airport_candidates" not in tool_names