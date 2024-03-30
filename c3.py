import subprocess, pathlib, os
C3_COMMAND = "c3"
dir = os.path.join(pathlib.Path(__file__).parent.resolve(), "todos")

class C3:
    command: list
    message: str
    def __init__(self, chat_id: int, message: str) -> None:
        self.command = ["c3", "-lnp", f"{dir}/{chat_id}", "--done-string","✅ ", "--undone-string", "❌ "]
        self.message = message

    def exec(self, *args) -> str:
        return subprocess.run([*self.command, *args], capture_output=True, text=True).stdout

    def print(self, *args) -> str:
        output = self.exec(*args)
        if not output:
            return "Empty todo list"

        return output

    def print_done(self) -> str:
        return self.print("-d")

    def append(self) -> str:
        return self.exec("-a", self.message)

    def search(self) -> str:
        return self.search_with_query(self.message)

    def search_with_query(self, query: str) -> str:
        return self.exec("-S", query)

    def set_done(self) -> str:
        self.exec("-S", self.message, "--done-selected")

        return self.print_done()

    def edit_message(self) -> str:
        self.exec("-S", self.message, "--done-selected")

        return self.print_done()

    def set_priority(self) -> str:
        try:
            first_space = self.message.index(' ')
            priority_str = self.message[:first_space]
            search = self.message[first_space+1:]
            priority = int(priority_str)
            if priority < 0 or priority > 9:
                return "Priority should be between 0 and 9"

            self.exec("-S", search, "--set-selected-priority", str(priority))

            return self.print()
        except Exception:
            return "Usage: <Priority [0,9]> <Message to search>"

    def delete(self) -> str:
        self.exec("-dS", self.message, "--delete-selected")

        return self.print_done()
