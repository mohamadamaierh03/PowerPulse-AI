from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from core.main_llm import basic_llm 
from .tools.dalle_tool import energy_visual_tool

@CrewBase
class PowerPulseCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def energy_planner(self) -> Agent:
        return Agent(config=self.agents_config['energy_planner'], llm=basic_llm, verbose=True)

    @agent
    def energy_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['energy_advisor'], 
            llm=basic_llm, 
            tools=[energy_visual_tool],
            verbose=True
        )

    @agent
    def technical_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_specialist'],
            llm=basic_llm,
            tools=[energy_visual_tool], 
            verbose=True,
            allow_delegation=False
        )



    @task
    def planning_task(self) -> Task:
        return Task(config=self.tasks_config['planning_task'])

    @task
    def consultation_task(self) -> Task:
        return Task(config=self.tasks_config['consultation_task'])

    @task
    def technical_diagnosis_task(self) -> Task:
        return Task(config=self.tasks_config['technical_diagnosis_task'])



    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[
                self.planning_task(), 
                self.consultation_task(), 
                self.technical_diagnosis_task()
            ], 
            process=Process.sequential,
            verbose=True
        )