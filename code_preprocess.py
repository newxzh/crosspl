def skip_note(line, ext, flag):
    if ext in [".rb",".sh",".r",".py"]:
        if flag % 2 == 1:
            return True
        if line.startswith('#'):
            return True
        if "'''" in line or '"""' in line:
            return True
        return False

    elif ext in [".cpp",".cc",".java",".c",".js",".ts",".php",".rs",".kt",".swift",".scala",".dart"]:
        if line.startswith('//'):
            return True
        if flag % 2 == 1:
            return True
        if line.startswith('/*') and line.endswith('*/'):
            return True
        if line.startswith('*/'):
            return True
        return False

    elif ext in [".html",".m",".mm"]:
        if line.startswith("<!--") and line.endswith("-->"):
            return True
        if flag % 2 == 1:
            return True
        return False

    elif ext == ".as":
        if line.startswith(";") or line.startswith("#"):
            return True
        return False
    else:
        return False


if __name__ == "__main__":
    def process_file(file_path, ext):
        with open(file_path, 'r',encoding="utf-8") as file:
            flag = 0
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith("/*") or line.endswith("*/"):
                    flag += 1
                if line.startswith("'''") or line.endswith("'''"):
                    flag += 1
                if line.startswith('"""') or line.endswith('"""'):
                    flag += 1
                if line.startswith("<!--") or line.endswith("-->"):
                    flag += 1
                if skip_note(line, ext, flag):
                    continue
                print(line)
    process_file("D:\CAE\Repository\\rrrr_1xxx\\node_modules\socket.io-client\dist\socket.io.slim.dev.js",".js")
