# /bin/zsh
toilet -f smblock --metal "gen"
python run.py gen


toilet -f smblock --metal "semantic"
python run.py test CheckSuite