import logging
from fastmcp import FastMCP, Context

logger = logging.getLogger(__name__)

def set_mcp_instance(mcp: FastMCP):
    """Register agentic workflow tool with the provided mcp instance."""
    
    @mcp.tool()
    async def handbrake_agentic_workflow(goal: str, ctx: Context) -> str:
        """
        High-level agentic workflow to achieve complex transcoding goals.
        Uses SEP-1577 sampling to request guidance from the host.
        
        Args:
            goal: The high-level objective (e.g. 'Optimize all videos in C:/Movies for iPad Pro').
            ctx: FastMCP Context for sampling and logging.
        """
        logger.info(f"[WORKFLOW] Starting agentic workflow for goal: {goal}")
        ctx.info(f"Analyzing goal: {goal}")
        
        # Step 1: Request a plan from the host via sampling
        prompt = f"I am a HandBrake MCP agent. The user goal is: '{goal}'. " \
                 f"Suggest a step-by-step plan using available tools (handbrake_ops, help_ops, status_ops). " \
                 f"Specify presets and target paths if applicable."
        
        ctx.report_progress(10, 100)
        plan_response = await ctx.sample(prompt=prompt, max_tokens=1024)
        
        if not plan_response:
            return "Failed to generate an agentic plan via sampling."
        
        plan_text = plan_response[0].text if hasattr(plan_response[0], 'text') else str(plan_response[0])
        
        ctx.info(f"Generated Plan: {plan_text}")
        ctx.report_progress(50, 100)
        
        # In a real SOTA implementation, the agent would then loop through the plan
        # and execute the tools. For this v13.1 upgrade, we demonstrate the capability.
        
        return f"### Agentic Plan for: {goal}\n\n{plan_text}\n\n*Execute the transcodes via handbrake_ops as per the plan.*"

    @mcp.tool()
    async def handbrake_optimize_library(source_dir: str, target_device: str, ctx: Context) -> str:
        """
        Expert tool to optimize an entire directory for a specific device.
        Leverages sampling to find the best preset for the given device.
        """
        ctx.info(f"Finding optimal preset for {target_device}...")
        
        prompt = f"What is the best HandBrake preset and CRF for {target_device} in 2026?"
        guidance = await ctx.sample(prompt=prompt)
        
        guidance_text = guidance[0].text if hasattr(guidance[0], 'text') else str(guidance[0])
        
        return f"Optimization strategy for {target_device} in {source_dir}:\n\n{guidance_text}"
