pip install -r requirements.txt

test -f .env || cp .env.example .env

echo 'alias kamal='\''docker run -it --rm -v "${PWD}:/workdir" -v "${SSH_AUTH_SOCK}:/ssh-agent" -v /var/run/docker.sock:/var/run/docker.sock -e "SSH_AUTH_SOCK=/ssh-agent" ghcr.io/basecamp/kamal:v1.6.0'\''' >> ~/.zshrc
