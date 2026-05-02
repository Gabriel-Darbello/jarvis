from skills.__init__ import avaible_skills
import ollama, json, re

class JarvisBrain:
    def __init__(self, model_name, max_memory = 10):
        with open("./Jarvis.md", "r", encoding="utf-8") as system_prompt:
            content = system_prompt.read()

        self.memory = [{"role": "system", "content": content}]
        self.model = model_name
        self.avaible_skills = avaible_skills
        self.max_memory = max_memory

    def _get_llm_decision(self):
        format_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "anyOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "params": {"type": "object"},
                                    "destructive": {"type": "boolean"}
                                },
                                "required": ["skill_name", "params", "destructive"]
                            },
                            {"type": "null"}
                        ]
                },
                "finished": {"type": "boolean"},
                "message": {"type": "string"}
            },
            "required": ["action", "finished", "message"]
        }

        try:
            response = ollama.chat(
                model=self.model,
                messages= self.memory,
                format=format_schema
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro ao se comunicar com o modelo: {e}"

    def _clear_response(self, llm_output):
            error_fallback = {
                "action": None,
                "finished": True,
                "message": "Desculpe Gabriel, tive um erro ao processar meu raciocínio."
            }

            try:
                if "```json" in llm_output:
                    llm_output = llm_output.split("```json")[-1].split("```")[0].strip()

                match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    clean_response = json.loads(json_str)

                    action = clean_response.get("action")

                    if isinstance(action, dict):
                        skill_name = action.get("skill_name")
                        if skill_name:
                            skill_exists = any(s.__name__ == skill_name for s in self.avaible_skills)
                            if skill_exists:
                                if skill_name in ["FileDeleteSkill", "FolderDeleteSkill"]:
                                    clean_response["action"]["destructive"] = True
                                return clean_response
                    return clean_response

                return error_fallback
            except Exception as e:
                print(f"Erro interno no parse: {e}")
                return error_fallback



    def _execute_skill(self, skill_name, params):
        skill_class = next((s for s in self.avaible_skills if s.__name__ == skill_name), None)

        if skill_class:
            try:
                skill_instance = skill_class()
                result = skill_instance.execute(params)
                return result
            except Exception as e:
                return f"Erro ao executar a skill {skill_name}: {e}"

        return "Skill não encontrada no sistema de execução."

    def _trim_memory(self):
        if len(self.memory) > self.max_memory + 1:
            self.memory = self.memory[0:1] + self.memory[-self.max_memory:]


    async def process_logic(self, user_input, callback_voice_confirm):
        self.memory.append({"role": "user", "content":user_input})

        while True:
            llm_response = self._get_llm_decision()
            self.memory.append({"role": "assistant", "content": llm_response})
            clean_llm_response = self._clear_response(llm_response)

            action = clean_llm_response.get("action") or {}
            skill_name = action.get("skill_name")
            params = action.get("params")
            if skill_name:
                if action.get("destructive"):
                    confirm = await callback_voice_confirm(clean_llm_response.get("message"))
                    if not confirm:
                        self.memory.append({"role": "user", "content": "Ação cancelada pelo usuário."})
                        continue
                llm_result = self._execute_skill(skill_name, params)
                self.memory.append({"role": "user", "content": f"Resultado da ação: {llm_result}"})
                continue

            if clean_llm_response.get("finished"):
                return clean_llm_response.get("message", "Tarefa concluída.")

            if not skill_name and not clean_llm_response.get("finished"):
                return "Erro de estado: O raciocínio foi interrompido sem uma conclusão clara."
