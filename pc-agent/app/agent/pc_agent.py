"""Main LangChain agent for PC build recommendations."""
from typing import Dict, Any, Optional
import structlog

from app.core.config import settings
from app.agent.tools import get_parts, check_compatibility, normalize_price, rate_performance

logger = structlog.get_logger()

# Try different import paths for LangChain compatibility
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
except ImportError:
    try:
        from langchain.agents.agent import AgentExecutor
        from langchain.agents.openai_tools import create_openai_tools_agent
    except ImportError:
        try:
            from langchain.agents.agent_executor import AgentExecutor
            from langchain.agents.openai_tools import create_openai_tools_agent
        except ImportError:
            # Fallback: use a simpler approach for Gemini
            AgentExecutor = None
            create_openai_tools_agent = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
except ImportError:
    ChatPromptTemplate = None
    MessagesPlaceholder = None


class PCBuildAgent:
    """LangChain agent for PC build recommendations."""
    
    SYSTEM_PROMPT = """You are an expert PC hardware consultant specializing in the Algerian market.
Your role is to help users build optimal PC configurations based on their budget, use case, and preferences.

You have access to a database of PC components available in Algeria (primarily from Ouedkniss.dz and local retailers).
All prices are in Algerian Dinar (DZD).

Your tools:
1. get_parts: Query components by type, price range, and specifications
2. check_compatibility: Verify that selected components work together
3. normalize_price: Convert prices to DZD if needed
4. rate_performance: Evaluate build performance for specific use cases

Guidelines:
- Always prioritize compatibility - a working build is better than a powerful incompatible one
- Consider the user's budget carefully - aim to use 90-100% of budget for best value
- Balance performance across components - avoid bottlenecks
- For gaming builds: prioritize GPU (50-60% of budget), then CPU (20-25%)
- For productivity: balance CPU and RAM, moderate GPU
- For AI/ML: prioritize GPU with high VRAM, strong CPU, and ample RAM (32GB+)
- Consider local availability and seller location when possible
- Explain your choices clearly in the user's preferred language (Arabic, French, or English)
- Provide alternatives when possible

Budget allocation guidelines:
- Gaming: GPU 50%, CPU 25%, RAM 10%, Storage 8%, PSU 5%, Case 2%
- Productivity: CPU 35%, RAM 20%, GPU 15%, Storage 20%, PSU 7%, Case 3%
- AI/ML: GPU 60%, CPU 15%, RAM 15%, Storage 7%, PSU 3%

Always verify compatibility before finalizing a build recommendation.
"""
    
    def __init__(self):
        """Initialize the PC build agent."""
        # Initialize LLM based on provider
        if settings.LLM_PROVIDER == "openai":
            if ChatOpenAI is None:
                raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                api_key=settings.OPENAI_API_KEY,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            self.use_direct_gemini = False
        elif settings.LLM_PROVIDER == "together":
            # Together AI for Mixtral
            try:
                from langchain_together import ChatTogether
                self.llm = ChatTogether(
                    model=settings.TOGETHER_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    together_api_key=settings.TOGETHER_API_KEY,
                    max_tokens=settings.LLM_MAX_TOKENS
                )
            except ImportError:
                # Fallback to community version
                from langchain_community.chat_models import ChatTogether
                self.llm = ChatTogether(
                    model=settings.TOGETHER_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    together_api_key=settings.TOGETHER_API_KEY,
                    max_tokens=settings.LLM_MAX_TOKENS
                )
            self.use_direct_gemini = False
        elif settings.LLM_PROVIDER == "gemini":
            # Google Gemini
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    google_api_key=settings.GEMINI_API_KEY,
                    max_output_tokens=settings.LLM_MAX_TOKENS
                )
                self.use_direct_gemini = False
            except ImportError:
                # Fallback: use google-generativeai directly
                logger.warning("langchain_google_genai not found, using direct Gemini API")
                self.llm = None
                self.use_direct_gemini = True
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
        
        # Define tools
        self.tools = [
            get_parts,
            check_compatibility,
            normalize_price,
            rate_performance
        ]
        
        # For Gemini with direct API, skip LangChain agent setup
        if settings.LLM_PROVIDER == "gemini" and self.use_direct_gemini:
            self.prompt = None
            self.agent = None
            self.executor = None
        elif AgentExecutor is None or create_openai_tools_agent is None or ChatPromptTemplate is None:
            # LangChain imports failed, use direct approach
            logger.warning("LangChain agent components not available, using direct LLM calls")
            self.prompt = None
            self.agent = None
            self.executor = None
        else:
            # Create prompt template
            try:
                self.prompt = ChatPromptTemplate.from_messages([
                    ("system", self.SYSTEM_PROMPT),
                    MessagesPlaceholder(variable_name="chat_history", optional=True) if MessagesPlaceholder else None,
                    ("user", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad") if MessagesPlaceholder else None,
                ])
            except Exception as e:
                logger.warning(f"Could not create prompt template: {str(e)}")
                self.prompt = None
            
            # Create agent
            if self.prompt and create_openai_tools_agent:
                try:
                    self.agent = create_openai_tools_agent(
                        llm=self.llm,
                        tools=self.tools,
                        prompt=self.prompt
                    )
                except Exception as e:
                    logger.warning(f"Could not create OpenAI tools agent: {str(e)}")
                    self.agent = None
            else:
                self.agent = None
            
            # Create executor
            if self.agent and AgentExecutor:
                try:
                    self.executor = AgentExecutor(
                        agent=self.agent,
                        tools=self.tools,
                        verbose=settings.DEBUG,
                        max_iterations=15,
                        handle_parsing_errors=True
                    )
                except Exception as e:
                    logger.warning(f"Could not create AgentExecutor: {str(e)}")
                    self.executor = None
            else:
                self.executor = None
        
        logger.info(f"PC Build Agent initialized with {settings.LLM_PROVIDER}")
    
    def recommend_build(
        self,
        budget_dzd: float,
        use_case: str,
        locale: str = "fr",
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a PC build recommendation.
        
        Args:
            budget_dzd: Budget in Algerian Dinar
            use_case: Primary use case (gaming, productivity, ai_ml, etc.)
            locale: Preferred language (ar, fr, en)
            preferences: Additional user preferences
            
        Returns:
            Build recommendation with components and explanation
        """
        try:
            # Construct user query
            locale_names = {"ar": "Arabic", "fr": "French", "en": "English"}
            language = locale_names.get(locale, "French")
            
            query = f"""
I need a PC build recommendation with the following requirements:

Budget: {budget_dzd:,.0f} DZD
Use Case: {use_case}
Preferred Language: {language}

Please recommend a complete PC build including:
- CPU (Processor)
- GPU (Graphics Card)
- Motherboard
- RAM (Memory)
- Storage (SSD/HDD)
- PSU (Power Supply)
- Case (optional, if budget allows)

For each component:
1. Use get_parts to find suitable options
2. Select the best value components that fit the budget
3. Verify compatibility with check_compatibility
4. Rate the final build with rate_performance

Provide your response in {language} with:
- Selected components with prices
- Total cost
- Compatibility status
- Performance rating for {use_case}
- Brief explanation of choices
"""
            
            if preferences:
                query += f"\n\nAdditional preferences: {preferences}"
            
            # Execute agent
            logger.info(f"Generating build for {budget_dzd} DZD, use case: {use_case}")
            
            if self.executor:
                # Use LangChain agent executor
                result = self.executor.invoke({"input": query})
                output = result.get("output", "")
            elif settings.LLM_PROVIDER == "gemini" and (hasattr(self, 'use_direct_gemini') and self.use_direct_gemini):
                # Use direct Gemini API with function calling
                output = self._call_gemini_with_tools(query)
            elif self.llm and hasattr(self.llm, 'invoke'):
                # Fallback: direct LLM call
                try:
                    response = self.llm.invoke(query)
                    output = response.content if hasattr(response, 'content') else str(response)
                except Exception as e:
                    logger.error(f"Error calling LLM: {str(e)}")
                    output = f"Error: {str(e)}"
            else:
                # Last resort: use direct Gemini
                if settings.LLM_PROVIDER == "gemini":
                    output = self._call_gemini_with_tools(query)
                else:
                    output = "Error: Could not execute agent - no executor or LLM available"
            
            return {
                "success": True,
                "recommendation": output,
                "budget_dzd": budget_dzd,
                "use_case": use_case,
                "locale": locale
            }
            
        except Exception as e:
            logger.error(f"Error generating build recommendation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "budget_dzd": budget_dzd,
                "use_case": use_case
            }
    
    def _call_gemini_with_tools(self, query: str) -> str:
        """Call Gemini API directly with function calling support."""
        try:
            import google.generativeai as genai
            from app.core.config import settings
            
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            
            # Create tools description for Gemini
            tools_description = """
Available tools:
1. get_parts(component_type, max_price_dzd, min_benchmark_score, condition, limit) - Query components
2. check_compatibility(component_ids) - Check component compatibility
3. normalize_price(price_str, source_currency) - Normalize prices
4. rate_performance(component_ids, use_case) - Rate build performance
"""
            
            # Enhanced prompt with tool descriptions
            enhanced_query = f"""{self.SYSTEM_PROMPT}

{tools_description}

User Request:
{query}

Please provide a detailed PC build recommendation. You can use the tools above to query the database for components.
"""
            
            # Call Gemini
            response = model.generate_content(enhanced_query)
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini directly: {str(e)}")
            return f"Error generating recommendation: {str(e)}"

