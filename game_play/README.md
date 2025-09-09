# Arctic Wargame Simulation

A multi-agent geopolitical simulation modeling Arctic resource competition between Russia, China, and the United States using AutoGen and Streamlit.

## 🎯 Overview

This simulation models the strategic competition for Arctic resources and shipping routes in the 2030s, where climate change has opened new opportunities for resource extraction and maritime commerce. Three AI agents represent the major powers, each with distinct goals and capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages (install with `pip install -r requirements.txt` from root directory)

### Running the Simulation

1. **Navigate to the game directory:**
   ```bash
   cd game_play
   ```

2. **Start the Streamlit application:**
   ```bash
   streamlit run arctic_wargame_app.py
   ```

3. **Open your browser:** The app will launch at `http://localhost:8501`

4. **Start playing:** Click "Start New Game" in the sidebar

## 🎮 How to Use

### Game Controls

**Starting a Game:**
- Click **"🚀 Start New Game"** to initialize all AI agents
- Wait for initialization confirmation

**Manual Play:**
- Click **"⏭️ Next Turn"** to advance one turn at a time
- Watch agent decisions and their consequences
- Monitor changing resource levels and tension

**Auto-Play Mode:**
- Toggle **"🔄 Auto-Play Mode"** for automated gameplay
- Adjust speed with the slider (1-10 seconds between turns)
- Click **"▶️ Start Auto-Play"** to begin automatic advancement

**Ending a Game:**
- Click **"🛑 End Game"** to stop the simulation
- This properly shuts down all agents

### Interface Components

#### Game Status Bar
- **Turn Counter**: Current turn number (each turn = ~6 months)
- **Tension Level**: Regional stability indicator (1-10 scale)
- **Phase Indicator**: Current situation assessment (Stable/Escalating/Critical)

#### Resource Dashboard
- **Bar Chart**: Visual comparison of all nations' resources
- **Resource Details**: Expandable panels showing exact values for each nation
- **Four Resource Types**:
  - **Military**: Armed forces, bases, equipment
  - **Economic**: Funding, trade relationships
  - **Political**: Domestic support, international standing  
  - **Information**: Intelligence quality, media influence

#### Recent Events Feed
- **Live Updates**: Real-time display of agent actions and consequences
- **Timestamped**: Events shown with simulated timestamps
- **Impact Indicators**: Success/failure of strategic actions

#### Victory Progress Tracker
- **Russia**: Progress toward controlling Arctic shipping routes
- **China**: Progress toward securing resource partnerships
- **United States**: Progress toward maintaining balance of power

## 🎯 Victory Conditions

### Russia 🇷🇺
- **Goal**: Control 60%+ of new Arctic shipping routes
- **Strategy**: Military presence and territorial claims
- **Key Actions**: Deploy fleets, establish bases, assert sovereignty

### China 🇨🇳  
- **Goal**: Secure 3+ major resource extraction partnerships
- **Strategy**: Economic investment and "Polar Silk Road"
- **Key Actions**: Infrastructure investment, diplomatic partnerships

### United States 🇺🇸
- **Goal**: Maintain balance of power (prevent domination)
- **Strategy**: NATO coordination and freedom of navigation
- **Key Actions**: Alliance building, counter-investments, military exercises

## 🧩 Game Mechanics

### Turn Structure
1. **Intelligence Phase**: Agents receive situation updates
2. **Decision Phase**: Each agent selects actions based on current state
3. **Action Phase**: All actions executed simultaneously
4. **Resolution Phase**: GameMaster calculates outcomes
5. **Update Phase**: Resources and tension levels adjusted

### Action Types

**Diplomatic Actions:**
- Negotiate agreements with other nations
- Participate in Arctic Council meetings
- Issue public statements

**Economic Actions:**
- Invest in infrastructure (ports, research stations)
- Offer resource extraction partnerships
- Impose economic sanctions

**Military Actions:**
- Deploy naval/air forces
- Conduct military exercises
- Establish permanent bases

**Information Actions:**
- Launch media campaigns
- Gather intelligence on rivals
- Conduct cyber operations

### Tension System
- **Level 1-3 (🟢 Stable)**: Normal diplomatic competition
- **Level 4-6 (🟡 Escalating)**: Increased posturing and tensions
- **Level 7-10 (🔴 Critical)**: Crisis mode with conflict risk

### Random Events
The GameMaster introduces random events (~30% chance per turn):
- Oil/gas discoveries in disputed waters
- Accelerated ice melting due to climate change
- Commercial shipping incidents
- International diplomatic interventions
- Environmental protests

## 🔧 Technical Architecture

### Core Components
- **arctic_agents.py**: Agent definitions and behaviors
- **game_engine.py**: Game state management and orchestration
- **arctic_wargame_app.py**: Streamlit user interface

### Agent Architecture
- **ArcticGameMaster**: Orchestrates game flow, manages state, introduces events
- **RussianAgent**: Focuses on military presence and territorial control
- **ChineseAgent**: Emphasizes economic partnerships and infrastructure
- **USAgent**: Prioritizes alliance coordination and balance of power

### Technologies Used
- **AutoGen**: Multi-agent conversation framework
- **Streamlit**: Web interface and real-time updates
- **Plotly**: Interactive charts and data visualization
- **Python AsyncIO**: Asynchronous agent communication

## 🎓 Educational Value

### Learning Objectives
- Understand Arctic geopolitical dynamics
- Explore multi-polar competition strategies
- Analyze resource-based conflicts
- Study escalation and de-escalation patterns

### Scenario Realism
Based on current Arctic developments:
- Russian Arctic militarization
- Chinese Belt and Road Arctic expansion
- US/NATO Arctic security initiatives
- Climate change impacts on navigation
- International law and territorial disputes

## 🐛 Troubleshooting

### Common Issues

**Game won't start:**
- Ensure all dependencies are installed
- Check that model_config.yml exists (will fallback to mock client if missing)
- Try restarting the Streamlit app

**Agents not responding:**
- Click "End Game" and start a new game
- Check console for error messages
- Ensure sufficient system resources

**Interface not updating:**
- Refresh the browser page
- Check network connection
- Restart the Streamlit server

### Performance Tips
- Close other browser tabs to free memory
- Use Chrome or Firefox for best performance
- Allow 2-3 seconds between manual turns for proper processing

## 🔄 Future Enhancements

### Planned Features
- Save/load game states
- More sophisticated AI decision making with LLM integration
- Additional random events and crisis scenarios
- Multiplayer mode (human + AI agents)
- Historical replay functionality
- Advanced visualization and maps

### Expansion Scenarios
- Cyber Infrastructure Crisis
- South China Sea Trade Disruption
- Space militarization competition
- Climate change refugee crisis

## 📚 References

This simulation is inspired by real-world Arctic developments and academic research on:
- Arctic Council policies and initiatives
- Russian Arctic strategy and Northern Sea Route development
- Chinese Polar Silk Road economic initiatives
- US/NATO Arctic security frameworks
- Climate change impacts on Arctic accessibility

---

**Note**: This is an educational simulation for understanding geopolitical dynamics. It does not predict actual future events or represent official policy positions of any nation.