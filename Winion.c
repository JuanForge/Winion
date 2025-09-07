#include <windows.h>
#include <stdio.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd) {
    char exePath[MAX_PATH];
    char dirPath[MAX_PATH];
    char command[1024];
    
    GetModuleFileName(NULL, exePath, MAX_PATH);
    
    strcpy(dirPath, exePath);
    char *lastSlash = strrchr(dirPath, '\\');
    if (lastSlash) *lastSlash = '\0';
    
    sprintf(command, "\"%s\\.Embeded\\Python.exe\" \"%s\\Main.pyc\"", dirPath, dirPath);
    
    for (int i = 1; i < __argc; i++) {
        strcat(command, " ");
        strcat(command, __argv[i]);
    }
    
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_SHOW;
    
    
    if (!CreateProcess(NULL, command, NULL, NULL, FALSE, 0, NULL, dirPath, &si, &pi)) {
        MessageBox(NULL, "Erreur lors du lancement de Python", "Erreur", MB_OK | MB_ICONERROR);
        return 22;
    }
    
    WaitForSingleObject(pi.hProcess, INFINITE);
    
    DWORD exitCode;
    GetExitCodeProcess(pi.hProcess, &exitCode);
    
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    
    return (int)exitCode;
}
