#include <windows.h>
#include <string>
#include <vector>

std::string GetExecutableDir() {
    char exePath[MAX_PATH] = {0};
    GetModuleFileNameA(NULL, exePath, MAX_PATH);
    std::string path(exePath);
    size_t pos = path.find_last_of("\\/");
    return (pos != std::string::npos) ? path.substr(0, pos) : path;
}

std::vector<char> MakeCommandLine(const std::string& command) {
    std::vector<char> buffer(command.begin(), command.end());
    buffer.push_back('\0');
    return buffer;
}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR lpCmdLine, int) {
    const std::string dirPath = GetExecutableDir();
    const std::string wtPath = dirPath + "\\Bin\\WindowsTerminal\\WindowsTerminal.exe";
    const std::string winionPath = dirPath + "\\Winion.exe";
    
    std::string cmdLine = "\"" + wtPath + "\" \"" + winionPath + "\"";
    if (lpCmdLine && *lpCmdLine) {
        cmdLine += " ";
        cmdLine += lpCmdLine;
    }
    
    std::vector<char> cmdBuffer = MakeCommandLine(cmdLine);
    
    STARTUPINFOA si{ sizeof(si) };
    PROCESS_INFORMATION pi{};
    
    if (!CreateProcessA(
            NULL,
            cmdBuffer.data(),
            NULL, NULL, FALSE, 0,
            NULL,
            dirPath.c_str(),
            &si, &pi)) 
    {
        MessageBoxA(NULL, "Impossible de lancer WindowsTerminal.exe", "Erreur", MB_OK | MB_ICONERROR);
        return 1;
    }
    
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    
    return 0;
}
