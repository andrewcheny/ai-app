import asyncio
import random
from typing import Dict, List, Optional
import yaml
from autogen_core import SingleThreadedAgentRuntime, AgentId
from autogen_core.models import ChatCompletionClient

from arctic_agents import (
    ArcticGameMaster, 
    RussianAgent, 
    ChineseAgent, 
    USAgent,
    GameState,
    ActionResultMessage,
    ActionType
)

class ArcticWargameEngine:
    def __init__(self):
        self.runtime: Optional[SingleThreadedAgentRuntime] = None
        self.game_master: Optional[ArcticGameMaster] = None
        self.agents: Dict[str, object] = {}
        self.is_initialized = False
        self.game_history: List[Dict] = []
        self.previous_actions: List[Dict] = []  # Track actions for reactive decisions
        self.human_player_mode = True  # Enable human control of United States
        self.discussion_history: List[Dict] = []  # Track discussion between human and AI
        self.current_suggestion: Optional[Dict] = None  # Current AI suggestion being discussed
        
    async def initialize(self):
        """Initialize the game engine with agents"""
        if self.is_initialized:
            return
            
        # Load model configuration
        try:
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            model_client = ChatCompletionClient.load_component(model_config)
        except Exception as e:
            # Fallback to mock client for testing
            model_client = None
            print(f"Warning: Could not load model client: {e}")
        
        # Create runtime
        self.runtime = SingleThreadedAgentRuntime()
        
        # Register agents with runtime using factory functions
        await ArcticGameMaster.register(self.runtime, "game_master", lambda: ArcticGameMaster(model_client))
        await RussianAgent.register(self.runtime, "russia", lambda: RussianAgent(model_client))
        await ChineseAgent.register(self.runtime, "china", lambda: ChineseAgent(model_client))
        await USAgent.register(self.runtime, "usa", lambda: USAgent(model_client))
        
        # Create a separate game master instance for direct access to game state
        # Note: This instance won't be able to publish messages, only provide game state
        self.game_master = ArcticGameMaster(model_client)
        
        self.is_initialized = True
        
    async def generate_opening_crisis(self) -> Dict:
        """Generate a dramatic opening crisis event"""
        crisis_scenarios = [
            {
                "name": "Arctic Environmental Disaster",
                "description": "Chinese oil tanker Shen Zhou carrying Russian Arctic crude oil suffers catastrophic hull breach during severe storm. 150,000 tons of oil spill into pristine Arctic waters, creating environmental crisis spanning three national territories.",
                "video_prompt": "Massive Chinese oil tanker breaking apart in violent Arctic storm, thick black oil spreading across pristine white ice sheets, emergency helicopters circling overhead, environmental disaster unfolding under dramatic aurora borealis, seabirds covered in oil struggling in freezing waters",
                "consequences": [
                    "Massive environmental cleanup required across international waters",
                    "Russia denies responsibility - claims Chinese navigation error", 
                    "China demands Russia pay for cleanup - oil was Russian property",
                    "Indigenous communities report contaminated fishing grounds",
                    "International environmental groups demand immediate action"
                ],
                "tension_increase": 2,
                "affected_resources": {
                    "russia_resources": {"political": -1, "economic": -2},
                    "china_resources": {"political": -2, "economic": -1}, 
                    "us_resources": {"political": 1}  # US gains moral authority
                }
            },
            {
                "name": "Arctic Submarine Collision",
                "description": "Russian nuclear submarine Komsomolsk collides with Chinese research vessel during covert Arctic mapping mission. Both crews rescued but classified technology scattered across Arctic seabed in disputed territorial waters.",
                "video_prompt": "Nuclear submarine surfacing through cracked Arctic ice in emergency, Chinese research vessel listing heavily with massive hull damage, military helicopters from multiple nations converging on scene, underwater footage of classified equipment sinking to ocean floor, tense rescue operations in blizzard conditions",
                "consequences": [
                    "Classified Russian naval technology exposed on seabed",
                    "China accuses Russia of ramming civilian research vessel",
                    "Russia claims Chinese ship was conducting espionage operations", 
                    "International salvage rights disputed across territorial claims",
                    "NATO monitoring Russian nuclear safety protocols"
                ],
                "tension_increase": 3,
                "affected_resources": {
                    "russia_resources": {"military": -2, "information": -1},
                    "china_resources": {"political": -1, "information": -2},
                    "us_resources": {"information": 2}  # US gains intelligence advantage
                }
            },
            {
                "name": "Arctic Cyber Infrastructure Attack",
                "description": "Massive cyber attack cripples Arctic shipping navigation systems during peak transit season. GPS satellites feeding false data, icebreaker fleets stranded, international shipping paralyzed. Attack origin unknown but sophisticated state-level operation suspected.",
                "video_prompt": "Multiple cargo ships and icebreakers dead in Arctic waters, navigation screens showing error messages, cyber warfare command centers with analysts frantically typing, satellite dishes and communication arrays sparking and going dark, ships' crews using manual navigation by stars over frozen landscape",
                "consequences": [
                    "International Arctic shipping completely paralyzed",
                    "Russia blames US cyber warfare capabilities",
                    "China accuses Russia of sabotaging Belt and Road shipping",
                    "US denies involvement but offers to investigate",
                    "Emergency international cyber security summit called"
                ],
                "tension_increase": 4,
                "affected_resources": {
                    "russia_resources": {"economic": -2, "information": -1},
                    "china_resources": {"economic": -3},
                    "us_resources": {"information": 1, "political": 1}
                }
            },
            {
                "name": "Arctic Resource Discovery Crisis", 
                "description": "Massive rare earth element deposit discovered directly on Russia-China-US territorial claim overlap. Geological surveys indicate deposit worth $2 trillion. All three nations immediately dispatch military forces to secure the area.",
                "video_prompt": "Geological survey teams in hazmat suits extracting mineral samples from pristine Arctic landscape, massive military convoys from three nations racing across frozen terrain toward same location, fighter jets from different countries circling overhead, heated diplomatic meetings with world maps showing territorial claims, military bases being rapidly constructed in harsh conditions",
                "consequences": [
                    "$2 trillion rare earth deposit spans disputed territorial waters",
                    "Russia immediately begins military base construction", 
                    "China deploys icebreaker fleet with mining equipment",
                    "US sends nuclear submarines to assert territorial claims",
                    "International law experts warn of potential armed conflict"
                ],
                "tension_increase": 5,
                "affected_resources": {
                    "russia_resources": {"military": 1, "economic": 2},
                    "china_resources": {"economic": 2, "political": 1},
                    "us_resources": {"military": 1, "political": 1}
                }
            },
            {
                "name": "Arctic Climate Tipping Point",
                "description": "Sudden acceleration of Arctic ice sheet collapse triggers unprecedented global climate event. Sea levels rise 2 meters overnight, new shipping lanes open, coastal cities flood. Nations scramble to adapt while exploiting new opportunities.",
                "video_prompt": "Massive ice sheets cracking and collapsing into ocean with thunderous roars, coastal cities with flood waters rushing through streets, emergency evacuations by helicopter, new open water shipping lanes revealed in previously frozen Arctic, nations' military ships racing toward newly accessible resources, dramatic time-lapse of changing Arctic map",
                "consequences": [
                    "Unprecedented Arctic shipping lanes suddenly open",
                    "Coastal flooding requires massive international response",
                    "New territorial water boundaries disputed globally", 
                    "Arctic resources become immediately accessible",
                    "Climate refugees create international crisis"
                ],
                "tension_increase": 3,
                "affected_resources": {
                    "russia_resources": {"economic": 3, "political": -1},
                    "china_resources": {"economic": 2, "political": -1},
                    "us_resources": {"political": -2, "military": 1}
                }
            }
        ]
        
        # Select random crisis or specific one if requested
        selected_crisis = random.choice(crisis_scenarios)
        
        # Try to enhance with AI if available
        try:
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            from autogen_core.models import ChatCompletionClient
            model_client = ChatCompletionClient.load_component(model_config)
            
            if model_client:
                enhanced_crisis = await self._enhance_crisis_with_ai(selected_crisis, model_client)
                return enhanced_crisis
                
        except Exception as e:
            print(f"AI enhancement unavailable, using predefined crisis: {e}")
        
        return selected_crisis
    
    async def _enhance_crisis_with_ai(self, base_crisis: Dict, model_client) -> Dict:
        """Enhance crisis description with AI for more dramatic effect"""
        system_prompt = """You are a military crisis correspondent reporting on breaking Arctic geopolitical events. Create intense, dramatic descriptions suitable for video generation.

Focus on:
- High-stakes international tensions
- Visual details for video production  
- Technical military and environmental specifics
- Emotional intensity and urgency
- Cinematic action sequences
- Geopolitical implications

Write in present tense with vivid, specific details."""

        user_prompt = f"""BREAKING CRISIS EVENT:
Title: {base_crisis['name']}
Base Description: {base_crisis['description']}

Enhance this crisis with:
1. More dramatic, cinematic description (3-4 sentences)
2. Enhanced video prompt with specific visual details
3. Additional immediate consequences that escalate tensions

Respond in JSON:
{{
    "enhanced_description": "dramatic cinematic description",
    "enhanced_video_prompt": "detailed video prompt with specific visuals, equipment, weather, action",
    "immediate_consequences": ["consequence 1", "consequence 2", "consequence 3"]
}}"""

        try:
            from autogen_core.models import SystemMessage, UserMessage
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            enhanced_content = json.loads(response_text)
            
            # Merge enhanced content with base crisis
            base_crisis['description'] = enhanced_content.get('enhanced_description', base_crisis['description'])
            base_crisis['video_prompt'] = enhanced_content.get('enhanced_video_prompt', base_crisis['video_prompt'])
            base_crisis['consequences'].extend(enhanced_content.get('immediate_consequences', []))
            
            return base_crisis
            
        except Exception as e:
            print(f"Error enhancing crisis with AI: {e}")
            return base_crisis

    async def start_game(self):
        """Start a new game with dramatic opening crisis"""
        if not self.is_initialized:
            await self.initialize()
            
        self.game_history = []
        
        # Generate and apply opening crisis
        opening_crisis = await self.generate_opening_crisis()
        self.opening_crisis = opening_crisis
        
        # Apply crisis effects to game state
        self.game_master._game_state.tension_level += opening_crisis['tension_increase']
        self.game_master._game_state.tension_level = min(10, self.game_master._game_state.tension_level)
        
        # Apply resource effects
        for nation, resource_changes in opening_crisis['affected_resources'].items():
            if nation == 'russia_resources':
                resources = self.game_master._game_state.russia_resources
            elif nation == 'china_resources':
                resources = self.game_master._game_state.china_resources
            elif nation == 'us_resources':
                resources = self.game_master._game_state.us_resources
            else:
                continue
                
            for resource_type, change in resource_changes.items():
                resources[resource_type] = max(0, min(10, resources[resource_type] + change))
        
        # Add crisis to recent events
        self.game_master._game_state.recent_events.append(f"🚨 BREAKING: {opening_crisis['name']}")
        self.game_master._game_state.recent_events.append(f"📰 {opening_crisis['description']}")
        
        # Add consequences
        for consequence in opening_crisis['consequences'][:3]:  # Limit to first 3 consequences
            self.game_master._game_state.recent_events.append(f"⚡ {consequence}")
        
        self.game_master._game_state.turn = 1
        
    async def execute_turn(self):
        """Execute one turn of the game"""
        if not self.is_initialized:
            return
            
        # Advance turn manually since we can't publish messages from this instance
        self.game_master._game_state.turn += 1
        
        # Simulate agent actions and return result
        return await self._simulate_agent_actions()
        
    def get_game_state(self) -> Optional[GameState]:
        """Get current game state"""
        if not self.game_master:
            return None
        return self.game_master.get_game_state()
        
    def get_game_history(self) -> List[Dict]:
        """Get game history"""
        return self.game_history
        
    async def _simulate_agent_actions(self):
        """Simulate agent actions with strategic reasoning and reactions"""
        turn = self.game_master._game_state.turn
        
        # Add turn reflections from previous actions
        if turn > 2 and self.previous_actions:
            self._add_turn_reflections()
        
        # Add random events occasionally
        if random.random() < 0.25:
            events = [
                "Massive oil deposit discovered in disputed Arctic waters",
                "Climate change accelerates Arctic ice melting", 
                "International Arctic Council calls emergency meeting",
                "Commercial shipping vessel reports harassment by military patrol",
                "Environmental activists protest Arctic drilling operations",
                "New shipping route opens through melting ice",
                "Submarine incident reported near North Pole",
                "Arctic research station establishes new base"
            ]
            self.game_master._game_state.recent_events.append(random.choice(events))
        
        # Track this turn's actions
        current_turn_actions = []
        
        # Simulate nation actions with reasoning
        nations = [
            ("Russia", self.game_master._game_state.russia_resources),
            ("China", self.game_master._game_state.china_resources), 
            ("United States", self.game_master._game_state.us_resources)
        ]
        
        # Process AI nations first (Russia and China work as alliance)
        ai_nations = [("Russia", self.game_master._game_state.russia_resources),
                     ("China", self.game_master._game_state.china_resources)]
        
        # Make Russia and China coordinate their actions (alliance behavior)
        for nation, resources in ai_nations:
            if random.random() < 0.8:  # 80% chance AI nations act (more aggressive)
                # Get action with alliance coordination
                action_with_reasoning = self._get_alliance_action(nation, resources, current_turn_actions)
                if action_with_reasoning:
                    action, reasoning = action_with_reasoning
                    
                    # Show reasoning
                    self.game_master._game_state.recent_events.append(
                        f"🧠 {nation} strategic thinking: {reasoning}"
                    )
                    
                    # Apply action effects
                    success = random.random() < 0.8  # Higher success rate for AI alliance
                    outcome = "succeeds" if success else "fails"
                    
                    # Generate dramatic description for AI action
                    dramatic_content = await self.generate_dramatic_action_description(action, success, nation)
                    
                    # Add dramatic action result
                    event_msg = f"⚡ {dramatic_content['dramatic_description']}"
                    self.game_master._game_state.recent_events.append(event_msg)
                    
                    # Store video prompt for potential use
                    action['generated_video_prompt'] = dramatic_content['video_prompt']
                    action['tactical_details'] = dramatic_content['tactical_details']
                    
                    # Track action for future reactions
                    current_turn_actions.append({
                        'nation': nation,
                        'action': action,
                        'success': success,
                        'turn': turn
                    })
                    
                    # Update resources
                    self._apply_action_effects(resources, action, success)
                    
                    # Update tension
                    self._update_tension(action, success, nation)
        
        # Check if human player (US) should act
        if self.human_player_mode:
            # Store current turn actions for human to see AI moves
            self.current_turn_actions = current_turn_actions
            return "human_action_needed"
        else:
            # AI mode - US acts automatically
            us_resources = self.game_master._game_state.us_resources
            if random.random() < 0.7:
                action_with_reasoning = self._get_strategic_action("United States", us_resources, current_turn_actions)
                if action_with_reasoning:
                    action, reasoning = action_with_reasoning
                    self.game_master._game_state.recent_events.append(f"🧠 United States strategic thinking: {reasoning}")
                    success = random.random() < 0.75
                    outcome = "succeeds" if success else "fails"
                    event_msg = f"⚡ United States {action['name']} {outcome}: {action['description']}"
                    self.game_master._game_state.recent_events.append(event_msg)
                    self._apply_action_effects(us_resources, action, success)
                    self._update_tension(action, success, "United States")
        
        # Store actions for next turn's reflections
        self.previous_actions = current_turn_actions
        
        # Keep only last 8 events (increased to accommodate reasoning)
        self.game_master._game_state.recent_events = self.game_master._game_state.recent_events[-8:]
        
        # Keep only last 5 adversary reactions and tension changes
        self.game_master._game_state.adversary_reactions = self.game_master._game_state.adversary_reactions[-5:]
        self.game_master._game_state.tension_changes = self.game_master._game_state.tension_changes[-5:]
        
        # Check for victory conditions
        victory_result = self._check_victory_conditions()
        if victory_result:
            self.game_master._game_state.recent_events.append(f"🏆 GAME OVER: {victory_result}")
            return "game_over"
        
        # Generate situation briefing
        briefing = self._generate_situation_briefing()
        if briefing:
            self.game_master._game_state.recent_events.append(f"📋 SITUATION BRIEFING: {briefing}")
        
        return None  # Normal turn completion
    
    def _get_strategic_action(self, nation: str, resources: Dict[str, int], current_turn_actions: List[Dict]) -> Optional[tuple]:
        """Get strategic action with reasoning based on current situation"""
        game_state = self.game_master._game_state
        tension = game_state.tension_level
        
        # Define nation-specific actions
        if nation == "Russia":
            actions = [
                {"type": ActionType.MILITARY, "name": "deploys Arctic fleet", "description": "Increases naval presence along Arctic shipping lanes", "cost": {"military": 2, "economic": 1}, "priority": "territorial_control"},
                {"type": ActionType.ECONOMIC, "name": "expands gas infrastructure", "description": "Builds new LNG terminals and pipelines", "cost": {"economic": 3}, "priority": "resource_dominance"},
                {"type": ActionType.DIPLOMATIC, "name": "proposes Arctic treaty", "description": "Suggests new framework for territorial claims", "cost": {"political": 2}, "priority": "legitimacy"},
                {"type": ActionType.INFORMATION, "name": "launches media campaign", "description": "Promotes Russian Arctic sovereignty claims", "cost": {"information": 2}, "priority": "narrative_control"}
            ]
        elif nation == "China":
            actions = [
                {"type": ActionType.ECONOMIC, "name": "invests in Arctic ports", "description": "Funds infrastructure development in partner nations", "cost": {"economic": 3}, "priority": "access_routes"},
                {"type": ActionType.DIPLOMATIC, "name": "strengthens Arctic partnerships", "description": "Negotiates resource extraction agreements", "cost": {"political": 2, "economic": 1}, "priority": "partnership_building"},
                {"type": ActionType.INFORMATION, "name": "promotes Belt and Road", "description": "Advocates for Polar Silk Road initiative", "cost": {"information": 2}, "priority": "strategic_narrative"},
                {"type": ActionType.MILITARY, "name": "conducts Arctic research mission", "description": "Sends icebreaker on 'scientific' expedition", "cost": {"military": 1, "economic": 2}, "priority": "presence_building"}
            ]
        else:  # United States
            actions = [
                {"type": ActionType.MILITARY, "name": "reinforces NATO Arctic presence", "description": "Increases joint exercises with Nordic allies", "cost": {"military": 2, "political": 1}, "priority": "alliance_strength"},
                {"type": ActionType.DIPLOMATIC, "name": "strengthens Arctic partnerships", "description": "Deepens cooperation with Arctic Council members", "cost": {"political": 3}, "priority": "multilateral_approach"},
                {"type": ActionType.ECONOMIC, "name": "invests in Arctic technology", "description": "Funds research into Arctic navigation and extraction", "cost": {"economic": 2, "information": 1}, "priority": "technological_edge"},
                {"type": ActionType.INFORMATION, "name": "promotes freedom of navigation", "description": "Challenges territorial claims through media", "cost": {"information": 2}, "priority": "legal_framework"}
            ]
        
        # Filter affordable actions
        affordable_actions = [a for a in actions if all(resources.get(r, 0) >= c for r, c in a['cost'].items())]
        if not affordable_actions:
            return None
        
        # Generate strategic reasoning and select action
        reasoning, selected_action = self._generate_strategic_reasoning(nation, affordable_actions, current_turn_actions, tension)
        
        return (selected_action, reasoning)
    
    def _generate_strategic_reasoning(self, nation: str, available_actions: List[Dict], current_turn_actions: List[Dict], tension: int) -> tuple:
        """Generate strategic reasoning for action selection"""
        game_state = self.game_master._game_state
        
        # Analyze what others have done this turn
        reactions = []
        for action_info in current_turn_actions:
            other_nation = action_info['nation']
            other_action = action_info['action']
            
            if other_action['type'] == ActionType.MILITARY:
                reactions.append(f"Responding to {other_nation}'s military posturing")
            elif other_action['type'] == ActionType.ECONOMIC:
                reactions.append(f"Countering {other_nation}'s economic expansion")
            elif other_action['type'] == ActionType.DIPLOMATIC:
                reactions.append(f"Matching {other_nation}'s diplomatic outreach")
        
        # Strategic reasoning based on nation and context
        reasoning_options = []
        
        if nation == "Russia":
            if tension >= 7:
                reasoning_options.extend([
                    "Escalating tensions require strong territorial assertion",
                    "Must demonstrate Arctic dominance amid growing competition"
                ])
            elif any("military" in str(a) for a in current_turn_actions):
                reasoning_options.append("Responding to military moves by rivals with force projection")
            else:
                reasoning_options.extend([
                    "Consolidating historical Arctic claims through strategic positioning",
                    "Leveraging natural resource advantages while competitors focus elsewhere"
                ])
        
        elif nation == "China":
            if any(a['nation'] == "Russia" and a['action']['type'] == ActionType.MILITARY for a in current_turn_actions):
                reasoning_options.append("Pursuing economic strategy while Russia focuses on military posturing")
            elif tension <= 3:
                reasoning_options.append("Low tensions create opportunity for partnership building")
            else:
                reasoning_options.extend([
                    "Building economic presence through strategic partnerships",
                    "Advancing Belt and Road objectives in Arctic region"
                ])
        
        else:  # United States
            if tension >= 6:
                reasoning_options.extend([
                    "High tensions require multilateral response to prevent conflict",
                    "Strengthening alliances to counter unilateral actions"
                ])
            elif any(a['action']['type'] == ActionType.MILITARY for a in current_turn_actions):
                reasoning_options.append("Military escalation by others demands strong allied response")
            else:
                reasoning_options.extend([
                    "Maintaining balance of power through diplomatic engagement",
                    "Preventing any single nation from dominating Arctic governance"
                ])
        
        # Add reaction-based reasoning
        if reactions:
            reasoning_options.extend(reactions)
        
        # Add resource-based reasoning
        if sum(game_state.russia_resources.values()) > sum(game_state.china_resources.values()) + sum(game_state.us_resources.values()):
            if nation != "Russia":
                reasoning_options.append("Countering Russia's resource advantage through coordinated action")
        
        # Select reasoning and corresponding action
        if reasoning_options:
            selected_reasoning = random.choice(reasoning_options)
        else:
            selected_reasoning = f"Pursuing {nation}'s core Arctic strategy objectives"
        
        # Select action that best matches the reasoning
        if "military" in selected_reasoning.lower() or "force" in selected_reasoning.lower():
            military_actions = [a for a in available_actions if a['type'] == ActionType.MILITARY]
            if military_actions:
                return (selected_reasoning, random.choice(military_actions))
        
        if "economic" in selected_reasoning.lower() or "partnership" in selected_reasoning.lower():
            economic_actions = [a for a in available_actions if a['type'] == ActionType.ECONOMIC]
            if economic_actions:
                return (selected_reasoning, random.choice(economic_actions))
        
        if "diplomatic" in selected_reasoning.lower() or "alliance" in selected_reasoning.lower():
            diplomatic_actions = [a for a in available_actions if a['type'] == ActionType.DIPLOMATIC]
            if diplomatic_actions:
                return (selected_reasoning, random.choice(diplomatic_actions))
        
        # Default: random selection
        return (selected_reasoning, random.choice(available_actions))
    
    def _add_turn_reflections(self):
        """Add reflections on previous turn's actions"""
        if not self.previous_actions:
            return
            
        # Analyze previous turn outcomes
        successes = [a for a in self.previous_actions if a['success']]
        failures = [a for a in self.previous_actions if not a['success']]
        
        reflections = []
        
        if successes:
            for action_info in successes[:2]:  # Limit to 2 reflections
                nation = action_info['nation']
                action = action_info['action']
                
                success_reflections = [
                    f"💭 {nation} reflects: Our {action['type'].value} strategy proved effective",
                    f"💭 {nation} analysis: Successful {action['name']} strengthens our position",
                    f"💭 {nation} assessment: {action['name']} achieved strategic objectives"
                ]
                reflections.append(random.choice(success_reflections))
        
        if failures:
            for action_info in failures[:1]:  # Limit to 1 failure reflection
                nation = action_info['nation']
                action = action_info['action']
                
                failure_reflections = [
                    f"💭 {nation} review: Failed {action['name']} requires strategic adjustment",
                    f"💭 {nation} lesson learned: {action['type'].value} approach needs refinement",
                    f"💭 {nation} adaptation: Reconsidering tactics after {action['name']} setback"
                ]
                reflections.append(random.choice(failure_reflections))
        
        # Add reflections to events
        for reflection in reflections:
            self.game_master._game_state.recent_events.append(reflection)
    
    def _generate_situation_briefing(self) -> str:
        """Generate a strategic situation briefing"""
        game_state = self.game_master._game_state
        turn = game_state.turn
        tension = game_state.tension_level
        
        # Calculate resource totals
        russia_total = sum(game_state.russia_resources.values())
        china_total = sum(game_state.china_resources.values())
        us_total = sum(game_state.us_resources.values())
        
        # Determine leading nation
        leaders = [("Russia", russia_total), ("China", china_total), ("United States", us_total)]
        leaders.sort(key=lambda x: x[1], reverse=True)
        leading_nation, leading_score = leaders[0]
        
        # Generate briefing based on turn milestones and conditions
        briefings = []
        
        # Turn-based briefings
        if turn == 2:
            briefings.append("Initial positioning phase complete. Nations are establishing their Arctic strategies.")
        elif turn == 5:
            briefings.append("Early competition intensifying as nations stake territorial and economic claims.")
        elif turn == 10:
            briefings.append("Mid-game dynamics emerging. Resource investments beginning to show strategic impact.")
        elif turn % 7 == 0:  # Every 7 turns
            briefings.append(f"{leading_nation} maintains strategic advantage with total resources of {leading_score}.")
        
        # Tension-based briefings
        if tension >= 8:
            briefings.extend([
                "CRISIS ALERT: Arctic tensions reaching dangerous levels. Risk of armed confrontation increasing.",
                "International observers warn of potential for military escalation in disputed waters.",
                "Emergency diplomatic channels activated as nations seek to prevent Arctic conflict."
            ])
        elif tension >= 6:
            briefings.extend([
                "Rising tensions creating instability in Arctic region. Military posturing increasing.",
                "Arctic Council calls for restraint as territorial disputes intensify.",
                "Commercial shipping companies report concerns over safety in contested waters."
            ])
        elif tension <= 2:
            briefings.extend([
                "Diplomatic efforts showing positive results. Arctic cooperation improving.",
                "Peaceful competition fostering regional stability and economic development.",
                "International community praises collaborative approach to Arctic governance."
            ])
        
        # Resource-based briefings
        if any(sum(resources.values()) < 15 for resources in [game_state.russia_resources, game_state.china_resources, game_state.us_resources]):
            briefings.append("Resource depletion becoming critical concern. Nations must balance expansion with sustainability.")
        
        # Victory condition briefings
        russia_military = game_state.russia_resources.get('military', 0)
        china_economic = game_state.china_resources.get('economic', 0) 
        us_political = game_state.us_resources.get('political', 0)
        
        if russia_military >= 8:
            briefings.append("Russia's military dominance in Arctic raising international concerns about territorial control.")
        if china_economic >= 8:
            briefings.append("China's economic influence expanding rapidly through Arctic infrastructure investments.")
        if us_political >= 8:
            briefings.append("United States successfully maintaining multilateral approach to Arctic governance.")
        
        # Strategic insights
        if turn % 5 == 0:  # Every 5 turns
            insights = [
                f"Current regional balance shows {leading_nation} leading with {leading_score} total resources.",
                f"Tension level at {tension}/10 indicates {'high instability' if tension >= 7 else 'moderate stability' if tension >= 4 else 'relative calm'}.",
                f"Turn {turn}: Arctic competition entering {'critical phase' if turn >= 15 else 'intensification period' if turn >= 8 else 'establishment phase'}."
            ]
            briefings.extend(insights)
        
        return random.choice(briefings) if briefings else ""
    
    def _check_victory_conditions(self) -> Optional[str]:
        """Check if any nation has achieved victory conditions"""
        game_state = self.game_master._game_state
        turn = game_state.turn
        
        # Don't check for victory too early
        if turn < 10:
            return None
        
        # Check individual victory conditions
        russia_victory = self._check_russia_victory()
        china_victory = self._check_china_victory()  
        us_victory = self._check_us_victory()
        
        # If multiple victories, determine winner by strength
        victors = []
        if russia_victory:
            victors.append(("Russia", russia_victory))
        if china_victory:
            victors.append(("China", china_victory))
        if us_victory:
            victors.append(("United States", us_victory))
        
        if len(victors) > 1:
            # Multiple victories - judge by overall strength
            return self._adjudicate_multiple_victories(victors)
        elif len(victors) == 1:
            nation, victory_type = victors[0]
            return f"{nation} achieves decisive victory through {victory_type}!"
        
        # Check for stalemate or maximum turns
        if turn >= 25:
            return self._adjudicate_final_outcome()
        
        # Check for elimination conditions
        elimination = self._check_elimination_conditions()
        if elimination:
            return elimination
        
        return None
    
    def _check_russia_victory(self) -> Optional[str]:
        """Check Russia's victory conditions"""
        resources = self.game_master._game_state.russia_resources
        
        # Condition 1: Military dominance (9+ military + control 60%+ of routes)
        if resources.get('military', 0) >= 9 and resources.get('political', 0) >= 6:
            return "Arctic territorial control"
        
        # Condition 2: Resource monopoly (8+ military + 7+ economic)
        if resources.get('military', 0) >= 8 and resources.get('economic', 0) >= 7:
            return "resource extraction dominance"
        
        return None
    
    def _check_china_victory(self) -> Optional[str]:
        """Check China's victory conditions"""
        resources = self.game_master._game_state.china_resources
        
        # Condition 1: Economic dominance (9+ economic + 3+ major partnerships)
        if resources.get('economic', 0) >= 9 and resources.get('political', 0) >= 6:
            return "Polar Silk Road completion"
        
        # Condition 2: Partnership network (8+ political + 7+ economic)
        if resources.get('political', 0) >= 8 and resources.get('economic', 0) >= 7:
            return "Arctic partnership network"
        
        return None
    
    def _check_us_victory(self) -> Optional[str]:
        """Check US victory conditions"""
        resources = self.game_master._game_state.us_resources
        
        # Condition 1: Multilateral balance (8+ political + prevent others from dominating)
        if resources.get('political', 0) >= 8:
            # Check that no other nation has achieved dominance
            russia_total = sum(self.game_master._game_state.russia_resources.values())
            china_total = sum(self.game_master._game_state.china_resources.values())
            us_total = sum(resources.values())
            
            if us_total >= russia_total and us_total >= china_total:
                return "multilateral Arctic governance"
        
        # Condition 2: Alliance strength (9+ military + 7+ political)
        if resources.get('military', 0) >= 9 and resources.get('political', 0) >= 7:
            return "NATO Arctic security framework"
        
        return None
    
    def _check_elimination_conditions(self) -> Optional[str]:
        """Check if any nation is eliminated due to resource depletion"""
        nations = [
            ("Russia", self.game_master._game_state.russia_resources),
            ("China", self.game_master._game_state.china_resources),
            ("United States", self.game_master._game_state.us_resources)
        ]
        
        eliminated = []
        for nation, resources in nations:
            if sum(resources.values()) <= 8:  # Critical resource depletion
                eliminated.append(nation)
        
        if len(eliminated) >= 2:
            # Multiple eliminations - last standing wins
            survivors = [n for n, _ in nations if n not in eliminated]
            if survivors:
                return f"{survivors[0]} wins by survival - competitors eliminated due to resource depletion"
        
        return None
    
    def _adjudicate_multiple_victories(self, victors: List[tuple]) -> str:
        """Adjudicate when multiple nations achieve victory conditions"""
        # Calculate comprehensive scores
        scores = []
        for nation, victory_type in victors:
            if nation == "Russia":
                resources = self.game_master._game_state.russia_resources
            elif nation == "China":
                resources = self.game_master._game_state.china_resources
            else:
                resources = self.game_master._game_state.us_resources
            
            # Weighted scoring based on victory type relevance
            military_score = resources.get('military', 0) * 1.5
            economic_score = resources.get('economic', 0) * 1.2
            political_score = resources.get('political', 0) * 1.3
            info_score = resources.get('information', 0) * 1.0
            
            total_score = military_score + economic_score + political_score + info_score
            scores.append((nation, victory_type, total_score))
        
        # Sort by score
        scores.sort(key=lambda x: x[2], reverse=True)
        
        winner, victory_type, score = scores[0]
        runner_up = scores[1][0] if len(scores) > 1 else "other competitors"
        
        return f"{winner} achieves dominant victory through {victory_type}! (Score: {score:.1f}, defeating {runner_up})"
    
    def _adjudicate_final_outcome(self) -> str:
        """Adjudicate final outcome when maximum turns reached"""
        # Calculate final scores
        russia_total = sum(self.game_master._game_state.russia_resources.values())
        china_total = sum(self.game_master._game_state.china_resources.values()) 
        us_total = sum(self.game_master._game_state.us_resources.values())
        
        scores = [
            ("Russia", russia_total),
            ("China", china_total),
            ("United States", us_total)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        winner, winning_score = scores[0]
        second, second_score = scores[1]
        third, third_score = scores[2]
        
        # Determine victory margin
        if winning_score - second_score >= 8:
            margin = "decisive"
        elif winning_score - second_score >= 4:
            margin = "clear"
        else:
            margin = "narrow"
        
        # Generate final adjudication
        tension = self.game_master._game_state.tension_level
        
        adjudication = f"""FINAL ADJUDICATION (Turn 25): {winner} achieves {margin} victory!
        
🥇 {winner}: {winning_score} total resources
🥈 {second}: {second_score} total resources  
🥉 {third}: {third_score} total resources

Final tension level: {tension}/10
Strategic assessment: {self._get_final_strategic_assessment(winner, margin, tension)}"""
        
        return adjudication
    
    def _get_final_strategic_assessment(self, winner: str, margin: str, tension: int) -> str:
        """Generate final strategic assessment"""
        assessments = {
            ("Russia", "decisive"): "Russia's military-first approach secured Arctic dominance through territorial control",
            ("Russia", "clear"): "Russian energy infrastructure and military presence established regional hegemony",
            ("Russia", "narrow"): "Russia edged out competitors through sustained pressure on Arctic claims",
            ("China", "decisive"): "China's Belt and Road strategy successfully transformed Arctic into economic sphere of influence",
            ("China", "clear"): "Chinese investment and partnerships outmaneuvered military-focused competitors", 
            ("China", "narrow"): "China's economic approach proved slightly more effective than military posturing",
            ("United States", "decisive"): "US multilateral strategy successfully prevented Arctic militarization while maintaining influence",
            ("United States", "clear"): "American alliance-building and diplomatic engagement secured favorable Arctic governance",
            ("United States", "narrow"): "US balance-of-power approach barely contained aggressive expansion by rivals"
        }
        
        assessment = assessments.get((winner, margin), f"{winner}'s strategy proved most effective in Arctic competition")
        
        if tension >= 8:
            assessment += ". High tensions suggest potential for future conflict despite current resolution."
        elif tension <= 3:
            assessment += ". Low final tensions indicate successful management of Arctic competition."
        
        return assessment
    
    def _get_alliance_action(self, nation: str, resources: Dict[str, int], current_turn_actions: List[Dict]) -> Optional[tuple]:
        """Get action for Russia-China alliance with coordination"""
        # Check what alliance partner did
        partner_actions = [a for a in current_turn_actions if a['nation'] in ['Russia', 'China'] and a['nation'] != nation]
        
        # Get regular strategic action but with alliance reasoning
        result = self._get_strategic_action(nation, resources, current_turn_actions)
        if not result:
            return None
            
        action, reasoning = result
        
        # Enhance reasoning with alliance coordination
        if partner_actions:
            partner_action = partner_actions[0]
            partner_nation = partner_action['nation']
            if partner_action['action']['type'] == ActionType.MILITARY:
                reasoning = f"Coordinating with {partner_nation}'s military action - {reasoning}"
            elif partner_action['action']['type'] == ActionType.ECONOMIC:
                reasoning = f"Supporting {partner_nation}'s economic strategy - {reasoning}"
            else:
                reasoning = f"Alliance coordination with {partner_nation} - {reasoning}"
        else:
            reasoning = f"Leading alliance initiative - {reasoning}"
        
        return (action, reasoning)
    
    def _apply_action_effects(self, resources: Dict[str, int], action: Dict, success: bool):
        """Apply action effects to resources"""
        for resource, cost in action['cost'].items():
            if resource in resources:
                resources[resource] = max(0, resources[resource] - cost)
                if success and random.random() < 0.3:  # Sometimes gain resources
                    resources[resource] = min(10, resources[resource] + 1)
    
    def _update_tension(self, action: Dict, success: bool, nation: str = ""):
        """Update tension based on action with reasoning"""
        old_tension = self.game_master._game_state.tension_level
        
        if action['type'] == ActionType.MILITARY:
            change = 2 if success else 1
            self.game_master._game_state.tension_level = min(10, old_tension + change)
            if self.game_master._game_state.tension_level > old_tension:
                reason = f"🌡️ Tension rises {old_tension}→{self.game_master._game_state.tension_level}: {nation} military action {'escalates' if success else 'attempts escalation of'} regional competition"
                self.game_master._game_state.tension_changes.append(reason)
                
        elif action['type'] == ActionType.CYBER:
            change = 3 if success else 2  # Cyber attacks are highly escalatory
            self.game_master._game_state.tension_level = min(10, old_tension + change)
            if self.game_master._game_state.tension_level > old_tension:
                reason = f"🌡️ Tension spikes {old_tension}→{self.game_master._game_state.tension_level}: {nation} cyber operations {'severely escalate' if success else 'escalate'} regional tensions"
                self.game_master._game_state.tension_changes.append(reason)
                
        elif action['type'] == ActionType.HYBRID:
            change = 2 if success else 1
            self.game_master._game_state.tension_level = min(10, old_tension + change)
            if self.game_master._game_state.tension_level > old_tension:
                reason = f"🌡️ Tension rises {old_tension}→{self.game_master._game_state.tension_level}: {nation} hybrid operations {'destabilize' if success else 'threaten'} regional stability"
                self.game_master._game_state.tension_changes.append(reason)
                
        elif action['type'] == ActionType.DIPLOMATIC and success:
            self.game_master._game_state.tension_level = max(1, old_tension - 1)
            if self.game_master._game_state.tension_level < old_tension:
                reason = f"🌡️ Tension decreases {old_tension}→{self.game_master._game_state.tension_level}: {nation} successful diplomacy reduces regional friction"
                self.game_master._game_state.tension_changes.append(reason)
                
        elif action['type'] == ActionType.INFORMATION:
            # Information warfare can increase tension slightly
            if not success and random.random() < 0.3:
                self.game_master._game_state.tension_level = min(10, old_tension + 1)
                if self.game_master._game_state.tension_level > old_tension:
                    reason = f"🌡️ Tension rises {old_tension}→{self.game_master._game_state.tension_level}: {nation} failed information campaign backfires, causing friction"
                    self.game_master._game_state.tension_changes.append(reason)
                    
        elif action['type'] == ActionType.INTELLIGENCE:
            # Intelligence operations can cause tension if detected
            if success and random.random() < 0.4:  # 40% chance of detection
                self.game_master._game_state.tension_level = min(10, old_tension + 1)
                if self.game_master._game_state.tension_level > old_tension:
                    reason = f"🌡️ Tension rises {old_tension}→{self.game_master._game_state.tension_level}: {nation} intelligence operations detected, causing diplomatic friction"
                    self.game_master._game_state.tension_changes.append(reason)
    
    def get_human_actions(self) -> List[Dict]:
        """Get available actions for human player (United States)"""
        us_resources = self.game_master._game_state.us_resources
        
        # More dramatic and tactical action options
        all_actions = [
            {"type": ActionType.MILITARY, "name": "Operation Arctic Shield", "description": "Deploy advanced F-22 Raptors and nuclear submarines to assert dominance over contested Arctic waters", "cost": {"military": 3, "economic": 1}, "video_prompt": "F-22 fighter jets screaming across icy Arctic skies, nuclear submarines breaking through thick ice sheets, military bases illuminated against aurora borealis"},
            
            {"type": ActionType.MILITARY, "name": "Arctic Strike Force Deployment", "description": "Establish forward operating bases with Aegis missile systems targeting adversary positions", "cost": {"military": 4, "political": 1}, "video_prompt": "Military helicopters landing on frozen tundra, soldiers in Arctic camouflage setting up missile launchers, radar systems spinning against stormy Arctic landscape"},
            
            {"type": ActionType.CYBER, "name": "Operation Digital Blizzard", "description": "Launch sophisticated cyber attack on adversary Arctic communication networks and navigation systems", "cost": {"information": 3, "military": 1}, "video_prompt": "Cyber warfare command center with screens showing Arctic map overlays, hackers typing rapidly, enemy radar systems going dark across the Arctic"},
            
            {"type": ActionType.INTELLIGENCE, "name": "Arctic Shadow Reconnaissance", "description": "Deploy stealth drones and special forces for covert surveillance of enemy installations", "cost": {"information": 4, "military": 1}, "video_prompt": "Black stealth drones flying low over Arctic terrain, special forces in white gear observing enemy bases through night vision, satellite imagery revealing hidden installations"},
            
            {"type": ActionType.DIPLOMATIC, "name": "Arctic Alliance War Council", "description": "Convene emergency NATO meeting to coordinate massive joint response against aggression", "cost": {"political": 3, "information": 1}, "video_prompt": "Tense diplomatic meeting in war room with world maps, military leaders in uniform pointing at Arctic positions, flags of allied nations surrounding strategic table"},
            
            {"type": ActionType.ECONOMIC, "name": "Arctic Economic Warfare", "description": "Impose devastating sanctions and freeze Arctic assets to cripple adversary operations", "cost": {"economic": 3, "political": 2}, "video_prompt": "Stock market screens showing red numbers plummeting, frozen bank accounts, cargo ships turned away from Arctic ports, economic analysts in crisis mode"},
            
            {"type": ActionType.HYBRID, "name": "Operation Arctic Storm", "description": "Coordinate multi-domain assault combining cyber, economic, and military pressure", "cost": {"military": 2, "economic": 2, "information": 2}, "video_prompt": "Split screen showing cyber attacks, military movements, and economic pressure simultaneously - ships, planes, missiles, and data streams converging on Arctic theater"},
            
            {"type": ActionType.INFORMATION, "name": "Arctic Truth Campaign", "description": "Launch massive propaganda offensive exposing adversary aggression to world media", "cost": {"information": 4}, "video_prompt": "News anchors reporting breaking news, satellite footage of enemy movements, social media feeds exploding with Arctic content, protesters holding signs supporting freedom"},
            
            {"type": ActionType.MILITARY, "name": "Arctic Nuclear Deterrent", "description": "Deploy nuclear-capable assets as ultimate deterrent against further escalation", "cost": {"military": 5, "political": 2}, "video_prompt": "Massive nuclear submarine surfacing through Arctic ice, ballistic missiles on mobile launchers in snowy landscape, military command centers with red alert status"},
            
            {"type": ActionType.INTELLIGENCE, "name": "Arctic Deep Strike", "description": "Conduct precision sabotage operations against critical enemy infrastructure", "cost": {"information": 3, "military": 2}, "video_prompt": "Elite special forces rappelling from helicopters in blizzard conditions, explosions at enemy facilities, power grids going dark across enemy territory"}
        ]
        
        # Filter actions the US can afford
        affordable_actions = []
        for action in all_actions:
            can_afford = all(us_resources.get(resource, 0) >= cost for resource, cost in action['cost'].items())
            if can_afford:
                affordable_actions.append(action)
        
        return affordable_actions
    
    async def get_us_ai_advisor_suggestions(self, available_actions: List[Dict]) -> Dict:
        """Get AI advisor suggestions for US player based on current situation"""
        if not hasattr(self, 'game_master') or not self.game_master:
            return {"suggestions": [], "analysis": "Game not initialized"}
        
        try:
            # Load model configuration for advisor
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            from autogen_core.models import ChatCompletionClient
            model_client = ChatCompletionClient.load_component(model_config)
        except Exception:
            model_client = None
        
        if not model_client:
            return {"suggestions": available_actions[:3], "analysis": "AI advisor offline - showing top available actions"}
        
        game_state = self.game_master._game_state
        
        # Create US strategic advisor prompt
        system_prompt = """You are the top military and strategic advisor to the US President for Arctic operations. Your role is to analyze the current Arctic situation and provide tactical recommendations.

You are an expert in:
- Military strategy and Arctic warfare
- Geopolitical analysis and threat assessment  
- Multi-domain operations (land, sea, air, cyber, space)
- Alliance coordination and diplomatic leverage
- Economic warfare and sanctions effectiveness
- Intelligence operations and covert actions

Your analysis should be sharp, direct, and focused on protecting US interests while managing escalation risks."""

        recent_events = "\n".join(game_state.recent_events[-5:]) if game_state.recent_events else "No recent events"
        adversary_reactions = "\n".join(game_state.adversary_reactions[-3:]) if game_state.adversary_reactions else "No adversary reactions"
        tension_changes = "\n".join(game_state.tension_changes[-3:]) if game_state.tension_changes else "No tension changes"
        
        # Get current turn AI actions
        ai_actions = getattr(self, 'current_turn_actions', [])
        ai_actions_summary = ""
        if ai_actions:
            ai_actions_summary = "\n".join([f"- {action['nation']}: {action['action']['name']} ({'SUCCESS' if action['success'] else 'FAILED'})" for action in ai_actions])
        else:
            ai_actions_summary = "No adversary actions this turn"
        
        user_prompt = f"""SITUATION BRIEFING - TURN {game_state.turn}
🚨 THREAT LEVEL: {game_state.tension_level}/10

ADVERSARY MOVES THIS TURN:
{ai_actions_summary}

RECENT INTELLIGENCE:
{recent_events}

ADVERSARY COMMUNICATIONS INTERCEPTS:
{adversary_reactions}

TENSION ANALYSIS:
{tension_changes}

US RESOURCES STATUS:
Military Assets: {game_state.us_resources.get('military', 0)}/10
Economic Power: {game_state.us_resources.get('economic', 0)}/10  
Political Capital: {game_state.us_resources.get('political', 0)}/10
Information Warfare: {game_state.us_resources.get('information', 0)}/10

ENEMY FORCE ESTIMATES:
Russia - Military: {game_state.russia_resources.get('military', 0)}/10, Economic: {game_state.russia_resources.get('economic', 0)}/10
China - Military: {game_state.china_resources.get('military', 0)}/10, Economic: {game_state.china_resources.get('economic', 0)}/10

Based on this intelligence, provide:
1. Top 3 recommended actions from the available options (explain why each is optimal for current situation)
2. Threat assessment of adversary capabilities and likely next moves
3. Strategic analysis of risks and opportunities

Respond in JSON format:
{{
    "top_recommendations": [
        {{"action_name": "name", "priority": "HIGH/MEDIUM/LOW", "rationale": "why this action now"}},
        ...
    ],
    "threat_assessment": "analysis of enemy threats and capabilities",
    "strategic_analysis": "risks, opportunities, and recommended approach",
    "urgency_level": "CRITICAL/HIGH/MODERATE/LOW"
}}

Be direct and tactical in your analysis."""

        try:
            from autogen_core.models import SystemMessage, UserMessage
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            advisor_analysis = json.loads(response_text)
            return advisor_analysis
            
        except Exception as e:
            print(f"Error in US AI advisor: {e}")
            # Fallback analysis
            return {
                "top_recommendations": [
                    {"action_name": available_actions[0]['name'] if available_actions else "No actions available", "priority": "HIGH", "rationale": "Immediate response needed to current threats"},
                    {"action_name": available_actions[1]['name'] if len(available_actions) > 1 else "Limited options", "priority": "MEDIUM", "rationale": "Secondary defensive measure"}
                ],
                "threat_assessment": f"Tension at {game_state.tension_level}/10. Adversary actions detected this turn.",
                "strategic_analysis": "Recommend immediate action to counter adversary moves and maintain strategic balance.",
                "urgency_level": "HIGH" if game_state.tension_level >= 7 else "MODERATE"
            }
    
    async def generate_dramatic_action_description(self, action: Dict, success: bool, nation: str) -> Dict:
        """Generate dramatic tactical description for video generation"""
        try:
            # Load model configuration
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            from autogen_core.models import ChatCompletionClient
            model_client = ChatCompletionClient.load_component(model_config)
        except Exception:
            model_client = None
        
        if not model_client:
            return {
                "dramatic_description": f"{nation} {action['name']} {'succeeds' if success else 'fails'}: {action['description']}",
                "video_prompt": action.get('video_prompt', f"{nation} conducting {action['name']} in Arctic environment"),
                "tactical_details": f"Operation {'completed successfully' if success else 'encountered difficulties'}"
            }
        
        outcome = "SUCCESS" if success else "FAILURE"
        tension = self.game_master._game_state.tension_level
        
        system_prompt = f"""You are a military correspondent reporting on Arctic warfare operations. Create dramatic, tactical descriptions suitable for video generation.

Focus on:
- Cinematic military action sequences
- Detailed tactical movements and equipment
- Environmental conditions (Arctic weather, ice, aurora)  
- Emotional intensity and stakes
- Technical military terminology
- Visual details for video production

Write in present tense, high-intensity style. Be specific about military assets, weather conditions, and tactical execution."""

        user_prompt = f"""OPERATION REPORT:
Nation: {nation}
Operation: {action['name']}
Type: {action.get('type', 'Unknown').value if hasattr(action.get('type'), 'value') else action.get('type', 'Unknown')}
Outcome: {outcome}
Description: {action['description']}
Tension Level: {tension}/10 ({"CRITICAL" if tension >= 8 else "HIGH" if tension >= 6 else "MODERATE" if tension >= 4 else "LOW"})

Create:
1. Dramatic tactical description (2-3 sentences, cinematic style)
2. Detailed video prompt for AI generation (focus on visuals, action, environment)
3. Technical tactical details (equipment, maneuvers, timing)

Respond in JSON:
{{
    "dramatic_description": "intense cinematic description of the operation",
    "video_prompt": "detailed visual prompt for video generation including environment, equipment, action sequences",
    "tactical_details": "technical military details of execution and results"
}}"""

        try:
            from autogen_core.models import SystemMessage, UserMessage
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            dramatic_content = json.loads(response_text)
            return dramatic_content
            
        except Exception as e:
            print(f"Error generating dramatic description: {e}")
            return {
                "dramatic_description": f"{nation} executes {action['name']} with {'decisive precision' if success else 'unexpected complications'}. Arctic winds howl as {'the operation achieves its objectives' if success else 'forces adapt to changing battlefield conditions'}.",
                "video_prompt": f"{nation} military forces operating in harsh Arctic conditions, {action['name']} {'successfully completed' if success else 'facing tactical challenges'}, dramatic Arctic landscape with aurora borealis",
                "tactical_details": f"Multi-domain operation utilizing {action.get('type', 'combined')} assets. Weather conditions: Extreme. Mission status: {'COMPLETE' if success else 'ONGOING'}."
            }
    
    async def execute_human_action(self, chosen_action: Dict):
        """Execute the human player's chosen action"""
        us_resources = self.game_master._game_state.us_resources
        
        # Show human reasoning
        reasoning = self._get_human_action_reasoning(chosen_action)
        self.game_master._game_state.recent_events.append(f"🧠 United States (YOU) strategic thinking: {reasoning}")
        
        # Apply action effects
        success = random.random() < 0.75  # Same success rate as AI
        outcome = "succeeds" if success else "fails"
        
        # Generate dramatic description and video prompt
        dramatic_content = await self.generate_dramatic_action_description(chosen_action, success, "United States")
        
        # Add dramatic action result
        event_msg = f"⚡ {dramatic_content['dramatic_description']}"
        self.game_master._game_state.recent_events.append(event_msg)
        
        # Store video prompt for UI access
        chosen_action['generated_video_prompt'] = dramatic_content['video_prompt']
        chosen_action['tactical_details'] = dramatic_content['tactical_details']
        
        # Store last executed action for UI access
        self.last_executed_action = chosen_action
        
        # Track action
        self.current_turn_actions.append({
            'nation': 'United States',
            'action': chosen_action,
            'success': success,
            'turn': self.game_master._game_state.turn
        })
        
        # Update resources
        self._apply_action_effects(us_resources, chosen_action, success)
        
        # Update tension
        self._update_tension(chosen_action, success, "United States")
        
        # Generate adversary reactions to US action
        self._generate_adversary_reactions(chosen_action, success)
        
        # Store actions for next turn
        self.previous_actions = self.current_turn_actions
        
        # Keep only last 8 events
        self.game_master._game_state.recent_events = self.game_master._game_state.recent_events[-8:]
        
        # Keep only last 5 adversary reactions and tension changes
        self.game_master._game_state.adversary_reactions = self.game_master._game_state.adversary_reactions[-5:]
        self.game_master._game_state.tension_changes = self.game_master._game_state.tension_changes[-5:]
        
        # Check for victory conditions
        victory_result = self._check_victory_conditions()
        if victory_result:
            self.game_master._game_state.recent_events.append(f"🏆 GAME OVER: {victory_result}")
            return "game_over"
        
        # Generate situation briefing
        briefing = self._generate_situation_briefing()
        if briefing:
            self.game_master._game_state.recent_events.append(f"📋 SITUATION BRIEFING: {briefing}")
        
        return "action_completed"
    
    def _get_human_action_reasoning(self, action: Dict) -> str:
        """Generate reasoning for human action based on current situation"""
        tension = self.game_master._game_state.tension_level
        
        # Analyze recent AI actions
        recent_ai_actions = [a for a in self.current_turn_actions if a['nation'] in ['Russia', 'China']]
        
        if recent_ai_actions:
            military_actions = [a for a in recent_ai_actions if a['action']['type'] == ActionType.MILITARY]
            economic_actions = [a for a in recent_ai_actions if a['action']['type'] == ActionType.ECONOMIC]
            
            if military_actions and action['type'] == ActionType.MILITARY:
                return f"Responding to Russia-China military coordination with defensive measures"
            elif economic_actions and action['type'] == ActionType.ECONOMIC:
                return f"Countering alliance economic expansion through competitive investment"
            elif action['type'] == ActionType.DIPLOMATIC:
                return f"Using diplomatic channels to address Russia-China alliance actions"
            elif action['type'] == ActionType.INFORMATION:
                return f"Challenging alliance narrative through information operations"
        
        # Default reasoning based on action type
        reasoning_map = {
            ActionType.MILITARY: f"Maintaining military balance against Russia-China alliance",
            ActionType.DIPLOMATIC: f"Pursuing multilateral approach to counter bilateral alliance",
            ActionType.ECONOMIC: f"Leveraging economic tools to maintain Arctic influence",
            ActionType.INFORMATION: f"Promoting democratic values against authoritarian partnership"
        }
        
        return reasoning_map.get(action['type'], "Pursuing core US Arctic strategy objectives")
    
    def _generate_adversary_reactions(self, us_action: Dict, success: bool):
        """Generate reactions from Russia and China to US action"""
        reactions = []
        
        # Russia reactions
        if us_action['type'] == ActionType.MILITARY:
            if success:
                reactions.extend([
                    "💬 Russia reacts: 'US military buildup threatens Arctic stability. We reserve right to strengthen defensive positions.'",
                    "💬 Russia warns: 'American militarization of Arctic violates regional cooperation principles. Moscow will respond appropriately.'",
                    "💬 Russia responds: 'NATO expansion in Arctic forces Russia to reconsider strategic deterrence measures.'"
                ])
            else:
                reactions.append("💬 Russia notes: 'Failed US military posturing demonstrates declining American capability in Arctic region.'")
                
        elif us_action['type'] == ActionType.DIPLOMATIC:
            if success:
                reactions.extend([
                    "💬 Russia dismisses: 'US diplomatic initiatives ignore established Arctic territorial realities. Empty gestures will not change facts.'",
                    "💬 Russia critiques: 'American multilateral approach seeks to limit legitimate Russian Arctic sovereignty. We reject such interference.'"
                ])
            else:
                reactions.append("💬 Russia observes: 'Diplomatic failures show US inability to understand Arctic geopolitical dynamics.'")
                
        elif us_action['type'] == ActionType.ECONOMIC:
            reactions.extend([
                "💬 Russia counters: 'US economic competition cannot match Russia's natural resource advantages in Arctic region.'",
                "💬 Russia responds: 'American economic pressure tactics will backfire. Arctic nations prefer reliable Russian partnerships.'"
            ])
        elif us_action['type'] == ActionType.INFORMATION:
            reactions.append("💬 Russia dismisses: 'US propaganda cannot change geographic reality of Russian Arctic presence and capabilities.'")
        
        # China reactions  
        if us_action['type'] == ActionType.MILITARY:
            if success:
                reactions.extend([
                    "💬 China expresses 'deep concern': 'US military escalation threatens peaceful Arctic development. China advocates dialogue over confrontation.'",
                    "💬 China calls for restraint: 'Militarization of Arctic contradicts international cooperation principles. All parties should exercise prudence.'"
                ])
            else:
                reactions.append("💬 China observes: 'US military stumbles demonstrate risks of confrontational approach. China offers stable partnership alternative.'")
                
        elif us_action['type'] == ActionType.DIPLOMATIC:
            if success:
                reactions.extend([
                    "💬 China welcomes dialogue but notes: 'True Arctic cooperation must include all stakeholders, not just traditional Western allies.'",
                    "💬 China responds: 'Belt and Road Arctic initiatives offer more inclusive development framework than US-led partnerships.'"
                ])
        elif us_action['type'] == ActionType.ECONOMIC:
            reactions.extend([
                "💬 China confident: 'Chinese Arctic investments provide superior infrastructure and long-term economic benefits.'",
                "💬 China positions: 'US economic restrictions cannot halt China's Arctic development partnerships. Win-win cooperation prevails.'"
            ])
        elif us_action['type'] == ActionType.INFORMATION:
            reactions.append("💬 China advocates: 'Facts speak louder than rhetoric. Arctic development requires practical cooperation, not ideological competition.'")
        
        # Add 1-2 random reactions
        if reactions:
            selected_reactions = random.sample(reactions, min(2, len(reactions)))
            for reaction in selected_reactions:
                self.game_master._game_state.adversary_reactions.append(reaction)
    
    def get_final_adjudication(self) -> str:
        """Generate final adjudication when game is manually ended"""
        return self._adjudicate_final_outcome()
    
    def get_last_action_video_prompt(self) -> Optional[str]:
        """Get the video prompt from the last executed action"""
        if hasattr(self, 'last_executed_action') and self.last_executed_action:
            return self.last_executed_action.get('generated_video_prompt')
        return None
    
    def get_last_action_tactical_details(self) -> Optional[str]:
        """Get the tactical details from the last executed action"""
        if hasattr(self, 'last_executed_action') and self.last_executed_action:
            return self.last_executed_action.get('tactical_details')
        return None
    
    async def get_ai_advisor_for_human_player(self) -> Dict:
        """Get AI advisor suggestions for the human player"""
        available_actions = self.get_human_actions()
        suggestion = await self.get_us_ai_advisor_suggestions(available_actions)
        # Store current suggestion for potential discussion
        self.current_suggestion = suggestion
        return suggestion
    
    def get_opening_crisis(self) -> Optional[Dict]:
        """Get the opening crisis that triggered the game"""
        return getattr(self, 'opening_crisis', None)
    
    def get_opening_crisis_video_prompt(self) -> Optional[str]:
        """Get the video prompt for the opening crisis"""
        if hasattr(self, 'opening_crisis') and self.opening_crisis:
            return self.opening_crisis.get('video_prompt')
        return None
    
    def get_opening_crisis_description(self) -> Optional[str]:
        """Get the dramatic description of the opening crisis"""
        if hasattr(self, 'opening_crisis') and self.opening_crisis:
            return self.opening_crisis.get('description')
        return None

    async def start_discussion_with_ai(self, human_question: str, suggested_action: str) -> Dict:
        """Start a discussion between human player and AI advisor about a suggested action"""
        try:
            # Load model configuration
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            from autogen_core.models import ChatCompletionClient
            model_client = ChatCompletionClient.load_component(model_config)
        except Exception:
            model_client = None

        if not model_client:
            return {
                "ai_response": "AI advisor is currently offline. Please proceed with your best judgment.",
                "confidence_level": "LOW",
                "maintains_recommendation": True
            }

        game_state = self.game_master._game_state
        
        # Get current suggestion context
        current_suggestion = self.current_suggestion or {}
        
        system_prompt = """You are the US President's top military and strategic advisor engaged in a critical discussion about Arctic operations. 

The human player (President) is challenging or questioning your recommendation. You must:

1. Defend your strategic reasoning with facts and analysis
2. Address their specific concerns directly 
3. Consider their perspective and potentially adjust your recommendation
4. Provide clear rationale for why your suggestion is optimal
5. Acknowledge valid points they raise about risks or alternatives
6. Maintain respect for the President's ultimate decision authority

Be professional, analytical, and willing to engage in genuine strategic debate. If the President raises valid concerns, acknowledge them and potentially modify your recommendation. Your goal is to help them make the best decision for US interests.

Respond as if you're in a real-time strategy meeting in the White House Situation Room."""

        # Create context about the current situation and suggestion
        recent_events = "\n".join(game_state.recent_events[-3:]) if game_state.recent_events else "No recent events"
        
        user_prompt = f"""SITUATION ROOM DISCUSSION - TURN {game_state.turn}

CURRENT THREAT LEVEL: {game_state.tension_level}/10

YOUR PREVIOUS RECOMMENDATION: {suggested_action}

PRESIDENT'S QUESTION/CONCERN: {human_question}

CURRENT STRATEGIC CONTEXT:
{recent_events}

US RESOURCE STATUS:
- Military: {game_state.us_resources.get('military', 0)}/10
- Economic: {game_state.us_resources.get('economic', 0)}/10  
- Political: {game_state.us_resources.get('political', 0)}/10
- Information: {game_state.us_resources.get('information', 0)}/10

ENEMY POSITIONS:
- Russia Military: {game_state.russia_resources.get('military', 0)}/10, Economic: {game_state.russia_resources.get('economic', 0)}/10
- China Military: {game_state.china_resources.get('military', 0)}/10, Economic: {game_state.china_resources.get('economic', 0)}/10

As the President's advisor, respond to their question/concern. Be prepared to:
- Defend your recommendation with strategic reasoning
- Address their specific concerns
- Consider alternative approaches they might be suggesting
- Potentially modify your recommendation if they raise valid points

Respond in JSON format:
{{
    "ai_response": "Your detailed response to the President's question/concern",
    "key_points": ["point 1", "point 2", "point 3"],
    "acknowledges_concerns": true/false,
    "maintains_recommendation": true/false,
    "alternative_suggestions": "any alternative approaches if recommendation changes",
    "confidence_level": "HIGH/MEDIUM/LOW",
    "risk_assessment": "updated risk analysis based on the discussion"
}}"""

        try:
            from autogen_core.models import SystemMessage, UserMessage
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            discussion_response = json.loads(response_text)
            
            # Store this discussion exchange
            self.discussion_history.append({
                "turn": game_state.turn,
                "human_input": human_question,
                "suggested_action": suggested_action,
                "ai_response": discussion_response,
                "timestamp": game_state.turn
            })
            
            return discussion_response
            
        except Exception as e:
            print(f"Error in AI discussion: {e}")
            # Fallback response
            return {
                "ai_response": f"I understand your concern about {human_question}. Let me reconsider... Based on current threat levels and our strategic position, I still believe this is our best option, but I'm open to discussing alternatives.",
                "key_points": ["Current threat requires immediate response", "Our resources support this action", "Delaying may give advantage to adversaries"],
                "acknowledges_concerns": True,
                "maintains_recommendation": True,
                "alternative_suggestions": "We could consider a more diplomatic approach first, though this may be less effective given current tensions.",
                "confidence_level": "MEDIUM",
                "risk_assessment": "All options carry risks in current situation. Recommend proceeding with caution."
            }

    async def continue_discussion(self, human_followup: str) -> Dict:
        """Continue the discussion with a follow-up question or challenge"""
        if not self.discussion_history:
            return {"ai_response": "No previous discussion to continue. Please start a new discussion."}
        
        # Get the last discussion context
        last_discussion = self.discussion_history[-1]
        
        try:
            # Load model configuration
            with open("/workspaces/ai-app/agentchat_streamlit/model_config.yml", "r") as f:
                model_config = yaml.safe_load(f)
            from autogen_core.models import ChatCompletionClient
            model_client = ChatCompletionClient.load_component(model_config)
        except Exception:
            model_client = None

        if not model_client:
            return {
                "ai_response": "AI advisor connection lost. Please make your decision based on available information.",
                "maintains_recommendation": True
            }

        game_state = self.game_master._game_state
        
        system_prompt = """You are continuing a strategic discussion with the President about Arctic operations. 

You have already provided your initial response to their concerns. Now they have a follow-up question or challenge.

Continue the discussion by:
1. Addressing their new point directly
2. Building on your previous response
3. Providing additional analysis if needed
4. Being willing to modify your position based on compelling arguments
5. Maintaining the professional advisor relationship

This is a real-time strategy discussion in the Situation Room. Be concise but thorough."""

        # Build conversation history
        conversation_context = f"""PREVIOUS DISCUSSION:
President's Initial Question: {last_discussion['human_input']}
Your Previous Response: {last_discussion['ai_response']['ai_response']}

President's Follow-up: {human_followup}"""

        user_prompt = f"""CONTINUING SITUATION ROOM DISCUSSION

{conversation_context}

Current situation remains:
- Tension Level: {game_state.tension_level}/10
- Turn: {game_state.turn}
- US Resources: Military {game_state.us_resources.get('military', 0)}, Economic {game_state.us_resources.get('economic', 0)}, Political {game_state.us_resources.get('political', 0)}

Address the President's follow-up question/concern and provide your continued analysis.

Respond in JSON format:
{{
    "ai_response": "Your response to the follow-up",
    "addresses_followup": true/false,
    "maintains_recommendation": true/false,
    "final_recommendation": "your final recommendation after this discussion",
    "confidence_level": "HIGH/MEDIUM/LOW"
}}"""

        try:
            from autogen_core.models import SystemMessage, UserMessage
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            followup_response = json.loads(response_text)
            
            # Update discussion history
            self.discussion_history[-1]["followup_questions"] = self.discussion_history[-1].get("followup_questions", [])
            self.discussion_history[-1]["followup_questions"].append({
                "human_followup": human_followup,
                "ai_response": followup_response
            })
            
            return followup_response
            
        except Exception as e:
            print(f"Error in follow-up discussion: {e}")
            return {
                "ai_response": "I understand your additional concerns. Given the complexity of this situation, I recommend we proceed with careful consideration of the risks you've identified.",
                "addresses_followup": True,
                "maintains_recommendation": True,
                "final_recommendation": "Proceed with original plan but with enhanced risk mitigation measures",
                "confidence_level": "MEDIUM"
            }

    def get_discussion_history(self) -> List[Dict]:
        """Get the history of discussions between human and AI"""
        return self.discussion_history

    def clear_current_discussion(self):
        """Clear the current discussion context (called after action is taken)"""
        self.current_suggestion = None
        # Keep discussion history for reference but clear current context

    async def shutdown(self):
        """Shutdown the game engine"""
        # Since we're using a simplified simulation approach without active agents,
        # we just need to clean up the state
        self.runtime = None
        self.game_master = None
        self.agents = {}
        self.is_initialized = False
        self.game_history = []
        self.previous_actions = []