import yaml
import subprocess
import os

def main():
    with open('dataset/repos.yaml', 'r') as f:
        repos = yaml.safe_load(f)
        
    os.makedirs('dataset/clones', exist_ok=True)
    
    for lang, repo_list in repos.items():
        lang_dir = os.path.join('dataset/clones', lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        for repo in repo_list:
            repo_name = repo['name']
            repo_url = repo['url']
            repo_path = os.path.join(lang_dir, repo_name)
            
            if os.path.exists(repo_path):
                print(f"Skipping {repo_name} (already cloned)")
            else:
                print(f"Cloning {repo_name}...")
                subprocess.run(['git', 'clone', repo_url, repo_path], check=True)

if __name__ == "__main__":
    main()
