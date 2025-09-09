# Multi-Agent Wargame Design Documentation

## Project Overview
Development of a multi-agent wargame simulation featuring Russia, China, and US as autonomous agents in geopolitical scenarios.

## Scenario Design

### Scenario 1: Arctic Resource Competition
**Setting**: 2030s, melting Arctic ice opens new shipping routes and resource extraction opportunities

**Initial Conditions**:
- Russia claims expanded Arctic territory and militarizes northern bases
- China seeks Arctic shipping access through "Polar Silk Road" investments  
- US strengthens NATO Arctic partnerships and military presence

**Potential Outcomes**:
- Diplomatic resolution through Arctic Council negotiations
- Economic competition leading to infrastructure race
- Military tensions escalating to naval standoffs

### Scenario 2: Cyber Infrastructure Crisis
**Setting**: Critical infrastructure cyberattacks of unknown origin

**Initial Conditions**:
- Power grids and financial systems face coordinated attacks
- Each nation's intelligence agencies investigate while suspecting others
- Economic markets destabilize globally

**Potential Outcomes**:
- Multilateral cyber security cooperation agreements
- Attribution leads to economic sanctions and retaliation
- Escalation to kinetic responses against cyber infrastructure

### Scenario 3: South China Sea Trade Disruption
**Setting**: Maritime incident blocks major shipping lanes

**Initial Conditions**:
- Collision between military vessels disrupts 30% of global trade
- China closes shipping lanes citing security concerns
- US organizes freedom of navigation coalition

**Potential Outcomes**:
- International arbitration and compensation agreements
- Regional military buildup and proxy conflicts
- New trade routes and economic bloc formations

## Framework Selection

**Chosen Framework**: AutoGen + Streamlit

**Rationale**:
- AutoGen already installed in project (`autogen-core`, `autogen-ext`)
- Excellent for multi-agent conversations and role-playing
- Built-in human-in-the-loop capabilities
- Streamlit provides rapid web interface development
- Minimal additional dependencies required

## Arctic Scenario Agent Architecture

### Core Agent Structure

#### Nation Agents

**RussianAgent**: Arctic territorial claims specialist
- **Resources**: High Arctic military presence, icebreaker fleet, energy reserves
- **Goals**: Expand territorial claims, secure shipping routes, maintain regional dominance
- **Constraints**: Economic sanctions impact, limited allies in region

**ChineseAgent**: Arctic economic expansion strategist  
- **Resources**: Belt and Road funding, commercial fleet, technology investments
- **Goals**: Secure Arctic shipping access, resource extraction partnerships, "Polar Silk Road"
- **Constraints**: No Arctic territory, dependent on international law

**USAgent**: Arctic security coordinator
- **Resources**: NATO alliances, advanced military tech, Coast Guard capabilities  
- **Goals**: Maintain freedom of navigation, counter rival expansion, protect allies
- **Constraints**: Domestic political pressure, alliance coordination needs

#### System Agents

**GameMasterAgent**: Scenario orchestrator
- Tracks game state, resources, timeline
- Introduces random events (ice melts, oil discoveries, accidents)
- Enforces international law and consequences

**MediaAgent**: Public opinion simulator
- Generates news headlines based on agent actions
- Influences domestic pressure on nation agents
- Creates information warfare opportunities

### Agent Capabilities & Tools

#### Action Categories

**Diplomatic Actions**:
- `negotiate_agreement()`: Bilateral/multilateral negotiations
- `join_arctic_council()`: International forum participation  
- `issue_statement()`: Public diplomatic positions

**Economic Actions**:
- `invest_infrastructure()`: Ports, bases, research stations
- `offer_partnership()`: Resource extraction deals
- `impose_sanctions()`: Economic pressure tools

**Military Actions**:
- `deploy_forces()`: Naval/air presence adjustments
- `conduct_exercises()`: Show of force demonstrations
- `establish_base()`: Permanent military installations

**Information Actions**:
- `media_campaign()`: Shape public opinion
- `intelligence_gathering()`: Monitor rival activities
- `cyber_operations()`: Infrastructure disruption

#### Resource Management
Each agent tracks:
- **Military Assets**: Ships, aircraft, bases
- **Economic Resources**: Funding, trade relationships  
- **Political Capital**: Domestic support, international standing
- **Information Assets**: Intelligence quality, media influence

## Game Mechanics Framework

### Turn Structure
1. **Intelligence Phase**: Agents receive situation updates
2. **Planning Phase**: Each agent decides 2-3 actions privately  
3. **Action Phase**: Actions executed simultaneously
4. **Resolution Phase**: GameMaster calculates outcomes and consequences
5. **Information Phase**: Public results shared, private intel distributed

### Victory Conditions
- **Russia**: Control 60%+ of new Arctic shipping routes
- **China**: Secure 3+ major resource extraction partnerships  
- **US**: Prevent any single nation from dominating Arctic (balance of power)

### Escalation Mechanics
- **Tension Level**: 1-10 scale affecting action success rates
- **International Pressure**: UN/NATO responses to aggressive actions
- **Economic Impact**: Trade disruption affects all players
- **Crisis Events**: Random incidents that force immediate responses

### Decision Framework
Agents use weighted decision trees considering:
- **Strategic Goals** (40%): Long-term objectives
- **Tactical Opportunities** (30%): Immediate advantages  
- **Risk Assessment** (20%): Potential consequences
- **Domestic Pressure** (10%): Public opinion constraints

## AutoGen Implementation Structure

### Message Types
```python
@dataclass
class GameStateMessage:
    turn: int
    tension_level: int
    resource_status: Dict[str, Any]
    recent_events: List[str]

@dataclass  
class ActionMessage:
    agent: str
    action_type: str
    target: str
    parameters: Dict[str, Any]

@dataclass
class IntelligenceMessage:
    recipient: str
    intel_type: str
    content: str
    reliability: float
```

### Agent Conversation Flow
1. **GameMaster** broadcasts `GameStateMessage` to all agents
2. Nation agents respond with `ActionMessage` to GameMaster
3. **GameMaster** processes actions and sends `IntelligenceMessage` updates
4. **MediaAgent** generates news based on public actions
5. Cycle repeats for next turn

### Human Player Integration
- **Observer Mode**: Watch AI agents play scenario
- **Advisor Mode**: Suggest actions to one nation agent  
- **Director Mode**: Control random events and crisis timing
- **Analyst Mode**: Receive all intelligence and provide briefings

### Streamlit Interface Components
- **Arctic Map**: Visual representation of territorial claims and assets
- **Action Timeline**: Chronological log of all major decisions
- **Resource Dashboard**: Current status of each nation's capabilities
- **Crisis Panel**: Breaking news and random event notifications
- **Negotiation Chat**: Real-time diplomatic communications

## Technical Implementation Benefits

**Realistic Constraints**: Each nation has authentic strengths/limitations  
**Multiple Win Conditions**: Different victory paths create interesting dynamics
**Scalable Complexity**: Can start simple and add more sophisticated mechanics
**Human Integration**: Multiple ways for users to engage with the simulation

## Next Steps
1. Implement basic agent classes
2. Create game state management system
3. Develop Streamlit interface components
4. Test Arctic scenario with basic interactions
5. Expand to other scenarios (Cyber Infrastructure, South China Sea)

## Additional Research Conducted

### PowerPoint Integration Tools
Researched AutoGen-compatible tools for extracting text from PowerPoint presentations to generate scenario briefings:
- **python-pptx**: Primary library for PPT text extraction
- **PowerPoint-Text-Extractor**: GitHub project for automated extraction
- **Online tools**: Aspose Parser, GroupDocs Parser, DocHub AI-powered extraction

This capability can be integrated to create dynamic scenario briefings from PowerPoint materials.