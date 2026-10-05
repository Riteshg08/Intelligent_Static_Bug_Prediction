import os
import glob

for f in glob.glob('frontend/src/**/*.jsx', recursive=True):
    new_f = f[:-4] + '.tsx'
    if os.path.basename(f) == 'Dashboard.jsx':
        new_f = os.path.join(os.path.dirname(f), 'ProjectsView.tsx')
    print(f"Renaming {f} to {new_f}")
    os.rename(f, new_f)
