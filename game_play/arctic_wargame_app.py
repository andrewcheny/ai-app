import streamlit as st
import asyncio
import plotly.express as px
import pandas as pd
from datetime import datetime
import time

from game_engine import ArcticWargameEngine
from arctic_agents import GameState

# Configure page
st.set_page_config(
    page_title="Arctic Wargame Simulation",
    page_icon="🧊",
    layout="wide"
)


# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = ArcticWargameEngine()
    st.session_state.game_active = False
    st.session_state.auto_play = False
    st.session_state.human_action_needed = False
    st.session_state.available_actions = []
    st.session_state.final_adjudication = None
    st.session_state.discussion_mode = False
    st.session_state.current_discussion = None
    st.session_state.discussing_action = None

# Title and description
st.title("🧊 Arctic Resource Competition Wargame")
st.markdown("### 🎮 **Human vs AI**: You control 🇺🇸 United States against 🇷🇺 Russia-🇨🇳 China Alliance")

# Floating Game Controls Panel - Fixed at top of browser like menu bar
st.markdown("""
<style>
.floating-controls {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(38, 39, 48, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #464853;
    padding: 15px 20px;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.floating-controls .stButton button {
    width: 100%;
    margin: 0 5px;
}
.control-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 15px;
    max-width: 1200px;
    margin: 0 auto;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# Create floating controls container
st.markdown('<div class="floating-controls">', unsafe_allow_html=True)

# Game controls in floating panel
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if not st.session_state.game_active:
        if st.button("🚀 Start New Game", type="primary", key="floating_start"):
            with st.spinner("Initializing agents..."):
                try:
                    asyncio.run(st.session_state.engine.start_game())
                    st.session_state.game_active = True
                    st.success("Game started!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start game: {e}")
    else:
        if not st.session_state.human_action_needed:
            if st.button("⏭️ Next Turn", key="floating_next"):
                with st.spinner("Processing turn..."):
                    try:
                        result = asyncio.run(st.session_state.engine.execute_turn())
                        if result == "game_over":
                            st.session_state.game_active = False
                            st.success("Game completed! Check the final adjudication below.")
                        elif result == "human_action_needed":
                            st.session_state.human_action_needed = True
                            st.session_state.available_actions = st.session_state.engine.get_human_actions()
                            st.info("🇺🇸 Your turn! Choose an action for the United States below.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Turn execution failed: {e}")
        else:
            st.markdown("🇺🇸 **Your Action Needed**")

with col2:
    if st.session_state.game_active:
        if st.button("🛑 End Game", key="floating_end"):
            try:
                final_adjudication = st.session_state.engine.get_final_adjudication()
                asyncio.run(st.session_state.engine.shutdown())
                st.session_state.game_active = False
                st.session_state.final_adjudication = final_adjudication
                st.success("Game ended! Check the final adjudication below.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to end game: {e}")

with col3:
    st.session_state.auto_play = st.toggle("🔄 Auto-Play", value=st.session_state.auto_play, key="floating_autoplay")

with col4:
    if st.session_state.auto_play and st.session_state.game_active:
        auto_speed = st.slider("Speed (sec)", 1, 10, 3, key="floating_speed")
        if st.button("▶️ Start Auto-Play", key="floating_auto_start"):
            st.info("Auto-play activated!")

st.markdown('</div>', unsafe_allow_html=True)

# Add top padding to prevent content from being hidden behind floating controls
st.markdown("""
<style>
.main .block-container {
    padding-top: 120px !important;
}
</style>
""", unsafe_allow_html=True)

# No sidebar needed - Game controls are now floating at top

# Main game interface
if st.session_state.game_active:
    game_state = st.session_state.engine.get_game_state()
    
    if game_state:
        # Game status header
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Turn", game_state.turn)
        with col2:
            st.metric("Tension Level", f"{game_state.tension_level}/10", 
                     delta=None, delta_color="inverse")
        with col3:
            # Determine current phase
            if game_state.tension_level <= 3:
                phase = "🟢 Stable"
            elif game_state.tension_level <= 6:
                phase = "🟡 Escalating"
            else:
                phase = "🔴 Critical"
            st.metric("Phase", phase)
        
        # Main layout: Left sidebar (Nation Resources), Main column (Situation Room), Right sidebar (events)
        left_sidebar, main_col, right_sidebar = st.columns([1, 2, 1])
        
        # Left sidebar - Nation Resources
        with left_sidebar:
            st.subheader("🏛️ Nation Resources")
            
            # Create resource comparison chart
            resources_data = []
            for nation, resources in [
                ("Russia", game_state.russia_resources),
                ("China", game_state.china_resources),
                ("United States", game_state.us_resources)
            ]:
                for resource_type, value in resources.items():
                    resources_data.append({
                        "Nation": nation,
                        "Resource": resource_type.title(),
                        "Value": value
                    })
            
            df = pd.DataFrame(resources_data)
            
            # Vertical resource comparison chart for sidebar
            fig = px.bar(df, x="Resource", y="Value", color="Nation",
                        title="Resource Comparison",
                        color_discrete_map={
                            "Russia": "#FF6B6B",
                            "China": "#FF0000", 
                            "United States": "#45B7D1"
                        })
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Main column - Situation Room moved up
        with main_col:
            st.subheader("🎯 Situation Room")
            
            # Get opening crisis if available
            opening_crisis = st.session_state.engine.get_opening_crisis()
            if opening_crisis:
                st.markdown("### 🚨 Current Crisis")
                
                # Crisis info in expandable containers
                with st.container():
                    st.markdown(f"**{opening_crisis['name']}**")
                    st.markdown(f"*{opening_crisis['description']}*")
                
                # Show consequences
                with st.expander("⚡ Immediate Consequences", expanded=True):
                    for i, consequence in enumerate(opening_crisis['consequences'][:5], 1):
                        st.markdown(f"{i}. {consequence}")
                
                # Show current strategic assessment
                with st.expander("📊 Strategic Assessment", expanded=True):
                    col_r, col_c, col_u = st.columns(3)
                    
                    with col_r:
                        st.markdown("**🇷🇺 Russia**")
                        for resource, value in game_state.russia_resources.items():
                            st.metric(resource.title(), value)
                    
                    with col_c:
                        st.markdown("**🇨🇳 China**")
                        for resource, value in game_state.china_resources.items():
                            st.metric(resource.title(), value)
                    
                    with col_u:
                        st.markdown("**🇺🇸 United States**")
                        for resource, value in game_state.us_resources.items():
                            st.metric(resource.title(), value)
            else:
                # If no opening crisis, show current situation
                st.info("Monitoring Arctic situation. No active crisis detected.")
                
                # Show basic strategic overview
                with st.expander("📊 Current Strategic Balance", expanded=True):
                    col_r, col_c, col_u = st.columns(3)
                    
                    with col_r:
                        st.markdown("**🇷🇺 Russia**")
                        total_rus = sum(game_state.russia_resources.values())
                        st.metric("Total Power", total_rus)
                        
                    with col_c:
                        st.markdown("**🇨🇳 China**")
                        total_chi = sum(game_state.china_resources.values())
                        st.metric("Total Power", total_chi)
                    
                    with col_u:
                        st.markdown("**🇺🇸 United States**")
                        total_us = sum(game_state.us_resources.values())
                        st.metric("Total Power", total_us)
        
        # Right sidebar - Recent Events
        with right_sidebar:
            st.markdown("### 📰 Recent Events")
            
            if game_state.recent_events:
                for i, event in enumerate(reversed(game_state.recent_events[-8:])):
                    # Add timestamp simulation
                    time_ago = f"{(i+1)*2}m ago"
                    
                    # Style different types of events
                    if "🚨" in event or "BREAKING" in event:
                        st.error(f"**{time_ago}**\n{event}")
                    elif "🧠" in event:
                        st.info(f"**{time_ago}**\n{event}")
                    elif "⚡" in event:
                        st.warning(f"**{time_ago}**\n{event}")
                    elif "📋" in event:
                        st.success(f"**{time_ago}**\n{event}")
                    else:
                        st.markdown(f"**{time_ago}**\n{event}")
            else:
                st.info("No recent events...")
            
            st.divider()
            
            # Adversary reactions in sidebar
            st.markdown("### 💬 Intel Reports")
            
            if game_state.adversary_reactions:
                for i, reaction in enumerate(reversed(game_state.adversary_reactions[-5:])):
                    time_ago = f"{(i+1)*3}m ago"
                    st.warning(f"**{time_ago}**\n{reaction}")
            else:
                st.info("No intercepted communications...")
            
            st.divider()
            
            # Tension changes in sidebar
            st.markdown("### 🌡️ Tension Monitor")
            
            if game_state.tension_changes:
                for i, change in enumerate(reversed(game_state.tension_changes[-3:])):
                    time_ago = f"{(i+1)*4}m ago"
                    if "rises" in change or "spikes" in change:
                        st.error(f"**{time_ago}**\n{change}")
                    else:
                        st.success(f"**{time_ago}**\n{change}")
            else:
                st.info("Tensions stable...")
        
        # Human action selection - now full width below main layout
        if st.session_state.human_action_needed and st.session_state.available_actions:
            st.divider()
            st.subheader("🇺🇸 US Strategic Command - Choose Your Action")
            
            # Show AI advisor suggestions first
            with st.expander("🧠 AI Strategic Advisor Analysis", expanded=True):
                try:
                    advisor_analysis = asyncio.run(st.session_state.engine.get_ai_advisor_for_human_player())
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**🚨 URGENCY: {advisor_analysis.get('urgency_level', 'UNKNOWN')}**")
                        
                        st.markdown("**📋 THREAT ASSESSMENT:**")
                        st.markdown(advisor_analysis.get('threat_assessment', 'Analysis unavailable'))
                        
                        st.markdown("**🎯 TOP RECOMMENDATIONS:**")
                        for i, rec in enumerate(advisor_analysis.get('top_recommendations', [])[:3], 1):
                            priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec.get('priority', ''), "⚪")
                            st.markdown(f"{i}. **{rec.get('action_name', 'Unknown')}** {priority_color} {rec.get('priority', 'UNKNOWN')}")
                            st.markdown(f"   *{rec.get('rationale', 'No rationale provided')}*")
                            
                            # Add discussion button for each recommendation
                            if st.button(f"💬 Discuss This Recommendation", key=f"discuss_{i}", help="Question or challenge this AI recommendation"):
                                st.session_state.discussion_mode = True
                                st.session_state.discussing_action = rec.get('action_name', 'Unknown')
                                st.rerun()
                    
                    with col2:
                        st.markdown("**🔍 STRATEGIC ANALYSIS:**")
                        st.markdown(advisor_analysis.get('strategic_analysis', 'No analysis available'))
                        
                except Exception as e:
                    st.warning(f"AI Advisor offline: {e}")
            
            # Discussion Interface
            if st.session_state.discussion_mode:
                st.divider()
                st.subheader("💬 Strategic Discussion with AI Advisor")
                st.markdown(f"**Discussing:** {st.session_state.discussing_action}")
                
                # Show discussion history if exists
                if st.session_state.current_discussion:
                    with st.expander("📜 Discussion History", expanded=True):
                        discussion = st.session_state.current_discussion
                        st.markdown(f"**Your Question:** {discussion.get('human_input', '')}")
                        st.markdown(f"**AI Response:** {discussion.get('ai_response', {}).get('ai_response', '')}")
                        
                        # Show follow-ups if any
                        followups = discussion.get('followup_questions', [])
                        for i, followup in enumerate(followups, 1):
                            st.markdown(f"**Your Follow-up {i}:** {followup.get('human_followup', '')}")
                            st.markdown(f"**AI Response {i}:** {followup.get('ai_response', {}).get('ai_response', '')}")
                
                # Input for discussion
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    discussion_input = st.text_area(
                        "Ask the AI advisor about this recommendation:",
                        placeholder="Example: 'Why do you think bombing this target is better than diplomatic pressure? Won't this escalate tensions and damage our international image?'",
                        height=100,
                        key="discussion_input"
                    )
                
                with col2:
                    st.markdown("**💡 Discussion Ideas:**")
                    st.markdown("• Question civilian casualties")
                    st.markdown("• Challenge escalation risks")
                    st.markdown("• Ask about alternatives")
                    st.markdown("• Probe strategic reasoning")
                    st.markdown("• Discuss international impact")
                
                # Discussion buttons
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    if st.button("🗣️ Start Discussion", disabled=not discussion_input):
                        with st.spinner("AI Advisor responding..."):
                            try:
                                response = asyncio.run(st.session_state.engine.start_discussion_with_ai(
                                    discussion_input, st.session_state.discussing_action
                                ))
                                st.session_state.current_discussion = {
                                    'human_input': discussion_input,
                                    'ai_response': response,
                                    'followup_questions': []
                                }
                                st.success("AI Advisor has responded!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Discussion failed: {e}")
                
                with col2:
                    if st.button("➕ Continue Discussion", disabled=not (st.session_state.current_discussion and discussion_input)):
                        with st.spinner("AI Advisor responding..."):
                            try:
                                response = asyncio.run(st.session_state.engine.continue_discussion(discussion_input))
                                # Add to current discussion
                                if 'followup_questions' not in st.session_state.current_discussion:
                                    st.session_state.current_discussion['followup_questions'] = []
                                st.session_state.current_discussion['followup_questions'].append({
                                    'human_followup': discussion_input,
                                    'ai_response': response
                                })
                                st.success("AI Advisor has responded to your follow-up!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Follow-up discussion failed: {e}")
                
                with col3:
                    if st.button("✅ End Discussion"):
                        st.session_state.discussion_mode = False
                        st.session_state.current_discussion = None
                        st.session_state.discussing_action = None
                        st.session_state.engine.clear_current_discussion()
                        st.success("Discussion ended. You can now choose your action.")
                        st.rerun()
                
                # Show AI's current recommendation after discussion
                if st.session_state.current_discussion:
                    ai_response = st.session_state.current_discussion.get('ai_response', {})
                    if ai_response:
                        st.divider()
                        st.markdown("**🎯 AI Advisor's Current Position:**")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            maintains_rec = ai_response.get('maintains_recommendation', True)
                            if maintains_rec:
                                st.success("✅ **Maintains original recommendation**")
                            else:
                                st.warning("⚠️ **Has modified recommendation based on discussion**")
                            
                            if ai_response.get('alternative_suggestions'):
                                st.markdown("**Alternative Approach:**")
                                st.markdown(ai_response.get('alternative_suggestions', ''))
                        
                        with col2:
                            st.metric("Confidence Level", ai_response.get('confidence_level', 'UNKNOWN'))
                            
                            acknowledges = ai_response.get('acknowledges_concerns', False)
                            if acknowledges:
                                st.success("✅ Acknowledges your concerns")
                            else:
                                st.info("ℹ️ Stands by original analysis")
                
                st.divider()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("**Available Strategic Operations:**")
                
                # Display actions in a more tactical format
                for i, action in enumerate(st.session_state.available_actions):
                    action_key = f"action_{i}"
                    cost_str = ", ".join([f"{k}: {v}" for k, v in action['cost'].items()])
                    
                    # Create tactical action display
                    action_container = st.container()
                    with action_container:
                        col_action, col_button = st.columns([3, 1])
                        
                        with col_action:
                            st.markdown(f"**{action['name']}** ({action['type'].value.upper()})")
                            st.markdown(f"*{action['description']}*")
                            st.caption(f"Cost: {cost_str}")
                            
                            # Show video prompt preview if available
                            if 'video_prompt' in action:
                                with st.expander("🎬 Operation Visual Preview"):
                                    st.markdown(action['video_prompt'])
                        
                        with col_button:
                            if st.button(f"Execute", key=action_key, type="primary"):
                                # Execute the chosen action
                                with st.spinner("Executing operation..."):
                                    try:
                                        result = asyncio.run(st.session_state.engine.execute_human_action(action))
                                        st.session_state.human_action_needed = False
                                        # Clear discussion mode when action is executed
                                        st.session_state.discussion_mode = False
                                        st.session_state.current_discussion = None
                                        st.session_state.discussing_action = None
                                        if result == "game_over":
                                            st.session_state.game_active = False
                                            st.success("Game completed! Check the final adjudication below.")
                                        else:
                                            st.success(f"Operation executed: {action['name']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Operation failed: {e}")
                    
                    st.divider()
            
            with col2:
                st.markdown("**🇺🇸 US Resources:**")
                for resource, value in game_state.us_resources.items():
                    color = "normal"
                    if value <= 2:
                        color = "inverse"
                    st.metric(resource.title(), value, delta_color=color)
        
        # Video Generation Prompt Section - Bottom of page
        st.divider()
        
        # Check for opening crisis video prompt
        opening_crisis = st.session_state.engine.get_opening_crisis()
        last_action_prompt = st.session_state.engine.get_last_action_video_prompt()
        last_action_tactical = st.session_state.engine.get_last_action_tactical_details()
        
        if opening_crisis or last_action_prompt:
            st.subheader("🎬 Video Generation Prompts")
            
            # Opening crisis video prompt
            if opening_crisis:
                with st.expander("🚨 Opening Crisis - Video Generation Prompt", expanded=True):
                    st.markdown(f"**Scene: {opening_crisis['name']}**")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**📝 Video Prompt:**")
                        prompt_text = opening_crisis['video_prompt']
                        st.text_area("", value=prompt_text, height=150, key="crisis_prompt", 
                                   help="Copy this prompt for AI video generation")
                        
                        # Copy button simulation
                        if st.button("📋 Copy Opening Crisis Prompt", key="copy_crisis"):
                            st.success("Prompt copied! Use with RunwayML, Stable Video, Pika Labs, or other AI video generators")
                    
                    with col2:
                        st.markdown("**🎯 Scene Details:**")
                        st.markdown(f"**Crisis:** {opening_crisis['name']}")
                        st.markdown(f"**Tension Impact:** +{opening_crisis['tension_increase']}")
                        st.markdown(f"**Duration:** 30-60 seconds recommended")
                        st.markdown(f"**Style:** Cinematic, dramatic, news footage")
                        
                        st.markdown("**🎥 Recommended Settings:**")
                        st.code("""
Resolution: 1920x1080 or 1280x720
Frame Rate: 24-30 fps
Style: Realistic, documentary
Mood: Dramatic, urgent
Weather: Arctic storm conditions
Lighting: Natural + emergency lights
                        """)
            
            # Last action video prompt
            if last_action_prompt:
                with st.expander("⚡ Latest Action - Video Generation Prompt", expanded=False):
                    st.markdown("**Last Executed Action Video Prompt:**")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.text_area("", value=last_action_prompt, height=100, key="action_prompt",
                                   help="Copy this prompt for AI video generation")
                        
                        if st.button("📋 Copy Action Prompt", key="copy_action"):
                            st.success("Prompt copied! Ready for video generation")
                    
                    with col2:
                        if last_action_tactical:
                            st.markdown("**⚙️ Tactical Details:**")
                            st.markdown(last_action_tactical)
                        
                        st.markdown("**🎬 Video Tips:**")
                        st.markdown("• Use military/tactical style")
                        st.markdown("• Include Arctic environment")  
                        st.markdown("• Show equipment and personnel")
                        st.markdown("• 15-30 second clips work best")
        
        # Additional video generation resources
        with st.expander("🛠️ Video Generation Resources & Tips"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🎥 Recommended AI Video Tools:**")
                st.markdown("• **RunwayML Gen-3** - High quality, good for action")
                st.markdown("• **Stable Video Diffusion** - Open source option")
                st.markdown("• **Pika Labs** - Good for realistic scenes")
                st.markdown("• **Luma Dream Machine** - Latest technology")
                st.markdown("• **Kling AI** - Advanced physics")
                
            with col2:
                st.markdown("**💡 Generation Tips:**")
                st.markdown("• Add 'cinematic' and '4K' for quality")
                st.markdown("• Specify camera angles (wide shot, close-up)")
                st.markdown("• Include weather conditions")
                st.markdown("• Mention specific military equipment")
                st.markdown("• Use terms like 'documentary style' or 'news footage'")
        
        # Victory conditions tracker
        st.subheader("🎯 Victory Conditions Progress")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🇷🇺 Russia**: Control Arctic Routes")
            russia_progress = min(100, (game_state.russia_resources.get('military', 0) * 10))
            st.progress(russia_progress / 100)
            st.caption(f"Progress: {russia_progress}%")
        
        with col2:
            st.write("**🇨🇳 China**: Secure Resource Partnerships")
            china_progress = min(100, (game_state.china_resources.get('economic', 0) * 11))
            st.progress(china_progress / 100)
            st.caption(f"Progress: {china_progress}%")
        
        with col3:
            st.write("**🇺🇸 United States**: Maintain Balance")
            # Balance = preventing others from winning
            us_progress = min(100, (game_state.us_resources.get('political', 0) * 12))
            st.progress(us_progress / 100)
            st.caption(f"Progress: {us_progress}%")
        
        # Scenario briefing
        with st.expander("📋 Scenario Briefing", expanded=False):
            st.markdown("""
            **Arctic Resource Competition - 2030s**
            
            Climate change has opened new Arctic shipping routes and resource extraction opportunities. 
            Three major powers compete for influence:
            
            - **Russia** 🇷🇺: Claims expanded territory, militarizes northern bases
            - **China** 🇨🇳: Seeks shipping access through "Polar Silk Road" investments  
            - **United States** 🇺🇸: Strengthens NATO partnerships, maintains freedom of navigation
            
            **Resources:**
            - **Military**: Armed forces, bases, equipment
            - **Economic**: Funding, trade relationships, investments
            - **Political**: Domestic support, international standing
            - **Information**: Intelligence quality, media influence
            
            **Tension Levels:**
            - 🟢 1-3: Stable diplomatic competition
            - 🟡 4-6: Rising tensions, increased posturing
            - 🔴 7-10: Crisis mode, risk of conflict
            """)
        
        # Auto-play implementation
        if st.session_state.auto_play:
            # Auto-advance every few seconds
            placeholder = st.empty()
            placeholder.info("Auto-play mode: Next turn in 3 seconds...")
            time.sleep(3)
            try:
                asyncio.run(st.session_state.engine.execute_turn())
                st.rerun()
            except Exception as e:
                st.error(f"Auto-play error: {e}")
                st.session_state.auto_play = False
        
    else:
        st.error("Unable to retrieve game state. Please restart the game.")

# Display final adjudication if game ended
if st.session_state.final_adjudication:
    st.subheader("🏆 Final Game Adjudication")
    st.markdown(st.session_state.final_adjudication)
    
    if st.button("🔄 Start New Game"):
        st.session_state.final_adjudication = None
        st.session_state.engine = ArcticWargameEngine()
        st.session_state.game_active = False
        st.session_state.human_action_needed = False
        st.session_state.available_actions = []
        st.session_state.discussion_mode = False
        st.session_state.current_discussion = None
        st.session_state.discussing_action = None
        st.rerun()

elif not st.session_state.game_active:
    # Welcome screen
    st.markdown("""
    ## Welcome to the Arctic Wargame Simulation
    
    This interactive simulation models geopolitical competition in the Arctic region between three major powers:
    
    ### 🎮 How to Play
    1. **Start New Game** - Initialize the simulation with AI agents
    2. **Advance Turns** - Watch agents make strategic decisions
    3. **Monitor Progress** - Track resources, tensions, and victory conditions
    4. **Use Auto-Play** - Let the simulation run automatically
    
    ### 🎯 Victory Conditions
    - **Russia**: Control 60%+ of Arctic shipping routes through military presence
    - **China**: Secure 3+ major resource extraction partnerships through economic investment
    - **United States**: Maintain balance of power, prevent any single nation from dominating
    
    ### 📊 Key Mechanics
    - **Turn-based**: Each turn represents several months of real-time
    - **Resource Management**: Nations must balance military, economic, political, and information assets
    - **Tension System**: Actions affect regional stability (1-10 scale)
    - **Random Events**: Unexpected developments can change the strategic landscape
    
    Click **"Start New Game"** in the sidebar to begin!
    """)
    
    # Display scenario image placeholder
    st.image("https://via.placeholder.com/800x300/2E4057/FFFFFF?text=Arctic+Wargame+Simulation", 
             caption="Arctic Resource Competition Scenario")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Arctic Wargame Simulation | Built with AutoGen + Streamlit | Educational Purposes Only
</div>
""", unsafe_allow_html=True)