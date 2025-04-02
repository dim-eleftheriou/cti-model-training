import os

# Microsoft Visual Studio 2022 Community edition should be installed
try:
    os.system(r'cmd /c ""C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe" modify ^'
              r' --installPath "C:\Program Files\Microsoft Visual Studio\2022\Community" ^'
              r' --add Microsoft.Net.Component.4.8.SDK ^'
              r' --add Microsoft.Net.Component.4.7.2.TargetingPack ^'
              r' --add Microsoft.VisualStudio.Component.Roslyn.Compiler ^'
              r' --add Microsoft.Component.MSBuild ^'
              r' --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^'
              r' --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest ^'
              r' --add Microsoft.VisualStudio.Component.VC.CMake.Project ^'
              r' --add Microsoft.VisualStudio.Component.VC.CLI.Support ^'
              r' --add Microsoft.VisualStudio.Component.VC.Llvm.Clang ^'
              r' --add Microsoft.VisualStudio.ComponentGroup.ClangCL ^'
              r' --add Microsoft.VisualStudio.Component.Windows11SDK.22621 ^'
              r' --add Microsoft.VisualStudio.Component.Windows10SDK.19041 ^'
              r' --add Microsoft.VisualStudio.Component.UniversalCRT.SDK ^'
              r' --add Microsoft.VisualStudio.Component.VC.Redist.MSM"')
except:
    print("Please check if Microsoft Visual Studio 2022 Community edition is installed")

# os.system('pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126')
# os.system('pip install "unsloth[windows] @ git+https://github.com/unslothai/unsloth.git"')
# os.system('pip install evaluate rouge_score tensorboard scikit-learn absl-py matplotlib')