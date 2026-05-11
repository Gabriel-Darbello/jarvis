from skills.__init__ import avaible_skills
from skills.get_focus_app import GetFocusAppSkill
import ollama, json, re, threading, time, os

class JarvisBrain:
    def __init__(self, basic_model, pro_model, max_memory = 5):
        with open("./Jarvis.md", "r", encoding="utf-8") as system_prompt:
            content = system_prompt.read()
        self.context = None
        self.memory = [{"role": "system", "content": content}]
        self.pro_model = pro_model
        self.basic_model = basic_model
        self.model = self.basic_model
        self.max_memory = max_memory
        self.avaible_skills = avaible_skills
        self.projects = os.listdir("./Jarvis_brain/02_projects")

        threading.Thread(target=self._preload_model, daemon=True).start()

    def _preload_model(self):
        try:
            ollama.chat(
                model=self.model,
                messages= self.memory,
                stream=True,
                options={
                    "keep_alive": -1,
                    "temperature": 0.1,
                    "num_thread": 6
                }
            )

            print(f"\n[SISTEMA] {self.model} carregado e pronto!")
        except Exception as e:
            print(f"Erro no warmup: {e}")

    def _detect_context(self, user_input, focus_app):
        projects = self.projects

        for project_md in projects:
            project = project_md.replace(".md", "")
            if project in user_input.lower():
                self.context = project
                return project

            if project in focus_app["titulo"].lower():
                self.context = project
                return project

        return None

    def _resume_context(self):
        with open("./Jarvis_brain/03_memory/memory_instruction.md", "r", encoding="utf-8") as f:
            memory_instruction = f.read()
        self.memory.append({"role":"tool", "content":f"[INSTRUÇÕES TEMPORÁRIAS DO SISTEMA] Resuma essa conversa seguindo: {memory_instruction}"})
        response = ollama.chat(
            model=self.model,
            messages= self.memory,
            stream=False,
            options={
                "keep_alive": -1,
                "temperature": 0.1,
                "num_thread": 6
            }
        )

        return response['message']['content']

    def _save_resume(self, resume, previous_context):
        with open(f"./Jarvis_brain/03_memory/{previous_context}.md", 'a', encoding='utf-8') as file:
            file.write('\n' + resume)

    def _load_context(self):
        with open("./Jarvis.md", "r", encoding="utf-8") as system:
            system_prompt = system.read()
        with open(f"./Jarvis_brain/03_memory/{self.context}.md", "r", encoding="utf-8") as context:
            context_prompt = context.read()

        self.memory[0]["content"] = f"{system_prompt} \n {context_prompt}"

    def _get_llm_decision(self):
        format_schema = {
                "type": "object",
                "properties": {
                    "action": {
                        "type": ["object", "null"],
                        "properties": {
                            "skill_name": {"type": "string"},
                            "params": {"type": "object"},
                            "destructive": {"type": "boolean"}
                        }
                    },
                    "finished": {"type": "boolean"},
                    "message": {"type": "string"}
                },
                "required": ["action", "finished", "message"]
            }

        try:
            start_time = time.time()
            response = ollama.chat(
                model=self.model,
                messages= self.memory,
                format=format_schema,
                stream=True,
                options={
                    "keep_alive": -1,
                    "temperature": 0.1,
                    "num_thread": 6
                }
            )

            first_token_time = None
            full_response = ""
            for chunk in response:
                if first_token_time is None:
                    first_token_time = time.time() - start_time
                    print(f"--- Tempo até a primeira letra: {first_token_time:.2f}s ---")

                full_response += chunk['message']['content']

            total_time = time.time() - start_time
            print(f"--- Tempo total de geração: {total_time:.2f}s ---")
            return full_response
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
        focus_app = GetFocusAppSkill().execute()
        self.memory.append({"role": "user", "content": user_input})
        self.memory.append({"role": "tool", "content": f"[INSTRUÇÕES TEMPORÁRIAS DO SISTEMA] Janela em foco: {focus_app['resumo']}"})

        previous_context = self.context
        self._detect_context(user_input, focus_app)
        if previous_context != self.context and previous_context is not None:
            context_resume = self._resume_context()
            self._save_resume(context_resume, previous_context)
            self._clear_temporary_instructions()
            self._load_context()

        for _ in range(5):
            llm_response = self._get_llm_decision()
            print(f"\n[DEBUG LLM]: {llm_response}")
            self.memory.append({"role": "assistant", "content": llm_response})
            clean_llm_response = self._clear_response(llm_response)


            action = clean_llm_response.get("action") or {}
            skill_name = action.get("skill_name")
            params = action.get("params")

            pro_skills = ["FileAppendSkill",  "FileCreateSkill", "FileReadSkill"]
            self.model = self.pro_model if skill_name in pro_skills else self.basic_model

            if skill_name:
                if action.get("destructive"):
                    confirm = await callback_voice_confirm(clean_llm_response.get("message"))
                    if not confirm:
                        self.memory.append({"role": "tool", "content": "Ação cancelada pelo usuário."})
                        self._clear_temporary_instructions()
                        continue

                llm_result, skill_instruction = self._execute_skill(skill_name, params)
                llm_feedback = f"[RESULTADO DE {skill_name}] {llm_result}"

                if skill_instruction:
                    self.memory.append({"role": "tool", "content": "[INSTRUÇÕES TEMPORÁRIAS DO SISTEMA]" + skill_instruction})

                self.memory.append({"role": "tool", "content": llm_feedback})
                self._clear_temporary_instructions()

            if clean_llm_response.get("finished"):
                self._trim_memory()
                return clean_llm_response.get("message", "Tarefa concluída.")

            if not skill_name and not clean_llm_response.get("finished"):
                return "Erro de estado: O raciocínio foi interrompido sem uma conclusão clara."

        self._trim_memory()
        return "Erro: número máximo de iterações atingido."
