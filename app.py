import streamlit as st

from agent.agent import create_messages, run_agent_turn


st.set_page_config(
    page_title="Airport Investment Intelligence",
    page_icon="✈️",
    layout="wide",
)


if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = create_messages()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


with st.sidebar:
    st.title("✈️ Airport Intelligence")

    st.markdown(
        """
Analyze U.S. airports using operational,
passenger, and capacity data.
"""
    )

    st.divider()

    st.subheader("Data Sources")

    st.markdown(
        """
✓ AirLabs  
✓ BTS Aviation Data  
✓ airportsdata
"""
    )

    st.divider()

    st.subheader("Example Questions")

    st.markdown(
        """
- Compare LA and Santa Ana airport congestion.
- What percentage of flights out of Anchorage are long-haul?
- What is the unmet flight demand at SFO?
- Which New England airports are candidates for terminal expansion?
"""
    )

    st.divider()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.agent_messages = create_messages()
        st.session_state.chat_messages = []
        st.rerun()


st.title("Airport Investment Intelligence Agent")

st.caption(
    "Ask about airport congestion, flight mix, "
    "capacity pressure, and expansion candidates."
)


if not st.session_state.chat_messages:
    with st.chat_message("assistant"):
        st.markdown(
            """
Hi! I'm the **Airport Investment Intelligence Agent**.

I can help analyze airport congestion, flight mix, capacity pressure,
unmet demand, and expansion candidates.

Operational flight analysis may work for airports outside the U.S.,
while passenger and capacity analysis is currently focused on U.S. airports
because it relies on BTS data.

Try asking:
- Compare LA and Santa Ana airport congestion.
- Which New England airports are candidates for terminal expansion?
- What percentage of flights from Anchorage are long-haul?
"""
        )


for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input("Ask about an airport...")


if user_input:
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing aviation data..."):
            try:
                answer = run_agent_turn(
                    st.session_state.agent_messages,
                    user_input,
                )
            except Exception as error:
                answer = (
                    "I couldn't complete the request because an "
                    f"external service returned an error: {error}"
                )

        st.markdown(answer)

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": answer,
    })