from skills.__init__ import avaible_skills
from groq import Groq
import json, re, time, os, dotenv

class JarvisBrain:
    def __init__(self, max_memory = 5):
        with open("./Jarvis.md", "r", encoding="utf-8") as system_prompt:
            content = system_prompt.read()
        dotenv.load_dotenv()

        self.memory = [{"role": "system", "content": content}]
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.max_memory = max_memory
        self.avaible_skills = avaible_skills


    def _get_llm_decision(self):
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.memory,
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            total_time = time.time() - start_time
            print(f"--- Tempo total: {total_time:.2f}s ---")
            return response.choices[0].message.content

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
            skill_instruction = ""
            try:
                with open(f"./Jarvis_brain/01_skills/{skill_name}.md", "r", encoding="utf-8") as skill_md:
                    skill_instruction = skill_md.read()
            except FileNotFoundError:
                print(f"[AVISO] Arquivo {skill_name}.md não encontrado. Usando skill sem instrução extra.")

            try:
                skill_instance = skill_class()
                result = skill_instance.execute(params)
                return result, skill_instruction
            except Exception as e:
                return f"Erro ao executar a skill {skill_name}: {e}", ''

        return "Skill não encontrada no sistema de execução.", ''

    def _trim_memory(self):
        if len(self.memory) > self.max_memory + 1:
            self.memory = self.memory[0:1] + self.memory[-self.max_memory:]

    def _clear_temporary_instructions(self):
        self.memory = [
            m for m in self.memory
            if "[INSTRUÇÕES TEMPORÁRIAS DO SISTEMA]" not in m.get("content", "")
        ]


    async def process_logic(self, user_input, callback_voice_confirm):
        self._trim_memory()
        self.memory.append({"role": "user", "content": user_input})

        for _ in range(5):
            llm_response = self._get_llm_decision()
            print(f"\n[DEBUG LLM]: {llm_response}")
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
                        self._clear_temporary_instructions()
                        continue

                llm_result, skill_instruction = self._execute_skill(skill_name, params)
                llm_feedback = f"[RESULTADO DE {skill_name}] {llm_result}"

                if skill_instruction:
                    self.memory.append({"role": "user", "content": "[INSTRUÇÕES TEMPORÁRIAS DO SISTEMA]" + skill_instruction})

                self.memory.append({"role": "user", "content": llm_feedback})
                self._clear_temporary_instructions()

            if clean_llm_response.get("finished"):
                self._trim_memory()
                return clean_llm_response.get("message", "Tarefa concluída.")

            if not skill_name and not clean_llm_response.get("finished"):
                return "Erro de estado: O raciocínio foi interrompido sem uma conclusão clara."

        self._trim_memory()
        return "Erro: número máximo de iterações atingido."
