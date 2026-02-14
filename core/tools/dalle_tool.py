from crewai.tools import BaseTool
from openai import OpenAI
from django.conf import settings

class Dalle3EnergyVisualizer(BaseTool):
    name: str = "DALL-E 3 Energy Visualizer"
    description: str = (
        "Generates educational or technical illustrations for electrical issues. "
        "Use this when a visual explanation of a fault or safety setup is needed."
    )

    def _run(self, prompt: str) -> str:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            enhanced_prompt = f"Professional technical illustration of: {prompt}. Minimalist, safe, and educational style."
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            return f"Image generation failed: {str(e)}"

energy_visual_tool = Dalle3EnergyVisualizer()