import zipfile
import json

def parse_sb3(path):
    """
    .sb3 파일을 열어 project.json 내 Scratch 블록들을 추출합니다.
    """
    try:
        with zipfile.ZipFile(path, 'r') as zipf:
            data = zipf.read("project.json")
            project = json.loads(data)
    except (zipfile.BadZipFile, KeyError, json.JSONDecodeError):
        raise ValueError("잘못된 sb3 파일 또는 JSON 형식 오류입니다.")

    blocks = []
    for target in project.get("targets", []):
        for blk_id, blk in target.get("blocks", {}).items():
            blocks.append({
                "id": blk_id,
                "opcode": blk.get("opcode", ""),
                "fields": blk.get("fields", {}),
                "inputs": blk.get("inputs", {}),
                "next": blk.get("next"),
                "parent": blk.get("parent"),
                "topLevel": blk.get("topLevel", False)
            })
    return blocks


def safe_get_value(dct, *keys, default=None):
    """
    중첩된 딕셔너리에서 안전하게 값을 추출합니다.
    """
    for key in keys:
        if isinstance(dct, dict) and key in dct:
            dct = dct[key]
        else:
            return default
    return dct


def opcode_to_pyblock(opcode, fields, inputs=None, context=None):
    """
    opcode를 PyBlock 블록 정의로 변환합니다.
    context는 함수 이름 추적 등에 사용됩니다.
    """
    if inputs is None:
        inputs = {}
    result = None

    try:
        if opcode == "event_whenflagclicked":
            result = ("Start Program", {
                "template": "if __name__ == \"__main__\":\n{child_code}",
                "color": "#AED581",
                "nested": True
            })

        elif opcode == "control_repeat":
            times = safe_get_value(fields, "TIMES", 0, default="10")
            result = ("Repeat", {
                "template": f"for i in range({times}):\n{{child_code}}",
                "color": "#FFF9C4",
                "nested": True
            })

        elif opcode == "looks_say":
            msg = safe_get_value(fields, "MESSAGE", 0, default="Hello")
            result = ("Say", {
                "template": f'print("{msg}")',
                "color": "#FFE0B2",
                "nested": False
            })

        elif opcode == "pen_clear":
            result = ("Clear Drawing", {
                "template": "t.clear()",
                "color": "#80DEEA",
                "nested": False
            })

        elif opcode == "motion_movesteps":
            steps = safe_get_value(fields, "STEPS", 0, default="10")
            result = ("Move Forward", {
                "template": f't.forward({steps})',
                "color": "#B3E5FC",
                "nested": False
            })

        elif opcode == "event_whenkeypressed":
            key = safe_get_value(fields, "KEY_OPTION", 0, default="space")
            result = ("Key Event", {
                "template": '# on key "{key}" pressed:\n{child_code}',
                "color": "#D1C4E9",
                "nested": True
            })

        elif opcode == "data_setvariableto":
            name = safe_get_value(fields, "VARIABLE", 0, default="var")
            val = safe_get_value(inputs, "VALUE", 1, "value", default="0")
            result = ("Set Variable", {
                "template": f"{name} = {val}",
                "color": "#E1BEE7",
                "nested": False
            })

        elif opcode == "data_changevariableby":
            name = safe_get_value(fields, "VARIABLE", 0, default="counter")
            val = safe_get_value(inputs, "VALUE", 1, "value", default="1")
            result = ("Change Variable", {
                "template": f"{name} += {val}",
                "color": "#CE93D8",
                "nested": False
            })

        elif opcode == "procedures_definition":
            func_name = extract_custom_function_name(context, inputs)
            result = (f"Define {func_name}", {
                "template": f"def {func_name}():\n{{child_code}}",
                "color": "#FFCCBC",
                "nested": True
            })

        elif opcode == "procedures_call":
            func_name = safe_get_value(fields, "procName", 0, default="myFunction")
            result = (f"Call {func_name}", {
                "template": f"{func_name}()",
                "color": "#FFAB91",
                "nested": False
            })

    except Exception as e:
        print(f"[opcode 변환 오류] {opcode} → {e}")

    if result:
        return result

    return ("Unknown", {
        "template": f"# [Unmapped opcode: {opcode}]",
        "color": "#E0E0E0",
        "nested": False
    })


def extract_custom_function_name(blocks, inputs):
    """
    procedures_definition 블록에서 연결된 prototype을 추적하여 함수 이름 추출
    """
    prototype_id = safe_get_value(inputs, "custom_block", 1, default=None)
    if not prototype_id:
        return "myFunction"

    for blk in blocks:
        if blk["id"] == prototype_id and blk["opcode"] == "procedures_prototype":
            return safe_get_value(blk.get("fields", {}), "procName", 0, default="myFunction")

    return "myFunction"
