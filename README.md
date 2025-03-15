# Monorepo
- Be in repo ingest development: \
  **git checkout development**
- Add the individual repo to merge:\
  **git remote add emailStep git@github.com:IP-Sentinel/emailStep.git**
- Fetch it:\
  **git fetch emailStep**
- Merge it:\
  **git merge emailStep/master --allow-unrelated-histories** 
- Fix any issues:\
  **git mergetool** \
(https://stackoverflow.com/questions/161813/how-to-resolve-merge-conflicts-in-git-repository)
- commit fixes:\
  **git commit -m "fix whichever files"**
- push development to github:\
  **git push origin development**
- get main:\
  **git checkout main**
- merge development:\
  **git merge development**
- Push main to github:\
  **git push origin main**
- Back to ingest development:\
  **git checkout development**
- remove remote individual repo:\
  **git remote rm emailStep** 
