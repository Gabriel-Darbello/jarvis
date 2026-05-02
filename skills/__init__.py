from skills.close_app import CloseAppSkill
from skills.file_create import FileCreateSkill
from skills.file_delete import FileDeleteSkill
from skills.file_read import FileReadSkill
from skills.file_write import FileAppendSkill
from skills.folder_delete import FolderDeleteSkill
from skills.get_focus_app import GetFocusAppSkill
from skills.open_app import OpenAppSkill

avaible_skills = {
    CloseAppSkill,
    FileCreateSkill,
    FileDeleteSkill,
    FileReadSkill,
    FileAppendSkill,
    FolderDeleteSkill,
    GetFocusAppSkill,
    OpenAppSkill
}
