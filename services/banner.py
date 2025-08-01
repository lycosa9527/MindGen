#!/usr/bin/env python3
"""
MindGen Banner Module v0.1.0
Displays application banner and startup information
"""

import logging

logger = logging.getLogger(__name__)

def display_banner():
    """
    Display the MindGen v0.1.0 banner with application information.
    Uses logger for consistency with the rest of the application.
    """
    banner = """
================================================================================
    ███╗   ███╗██╗███╗   ██╗██████╗ ███╗   ███╗ █████╗ ████████╗███████╗
    ████╗ ████║██║████╗  ██║██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
    ██╔████╔██║██║██╔██╗ ██║██║  ██║██╔████╔██║███████║   ██║   █████╗  
    ██║╚██╔╝██║██║██║╚██╗██║██║  ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
    ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
================================================================================
                              AI-Powered Teaching Plan Generator
                              Multi-Agent Collaborative System
                              Powered by LangChain Framework
================================================================================
                              Version: v0.1.0 (Production Ready)
                              Status: Stable Release
                              Architecture: Flask + WebSocket + LangChain
================================================================================
                              Features:
                              • Three LLM Collaboration (Qwen, DeepSeek, GPT-4o)
                              • Iterative Quality-Driven Improvement
                              • Real-Time Progress Monitoring
                              • Professional Web Interface
                              • Comprehensive Error Handling
                              • Production-Grade Logging & Monitoring
================================================================================
"""
    try:
        # Use logger instead of print for consistency
        logger.info("MindGen v0.1.0 banner displayed")
        # Still print the banner for visual effect, but also log it
        print(banner)
    except Exception as e:
        # Fallback if banner display fails
        logger.warning(f"Failed to display banner: {str(e)}")
        logger.info("MindGen v0.1.0 Application Starting...")

if __name__ == "__main__":
    display_banner() 