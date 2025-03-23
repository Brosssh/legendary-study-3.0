# ✨ The Legendary Study ✨

This is the backend that collect EIDs from [Wasmegg](https://wasmegg-carpet.netlify.app/), process them and generate daily reports showing the legendary distribution across the playerbase. The reports can be accessed on the [Wasmegg Legendary Study](https://wasmegg-carpet.netlify.app/legendary-study/).  


## 🔐 EID Privacy and Security

As the developer, **I cannot see the EIDs** that this application uses. Your raw EID is only used to make API calls to the game server. Once the API call is made, **your EID is [obfuscated and hashed](https://github.com/Brosssh/legendary-study-3.0/blob/main/backend/utility.py#L22) before being stored**, ensuring that it cannot be reversed. The hashed string can't be reversed, but it can still uniquely identify the same user. Each time the EID is submitted, the hashed key will remain consistent.


## 🚨  Cheating considerations

As we know, cheaters exists and it's possible to cheat in a variety of way. **Players using widely known cheating methods have been excluded from the study**; however, there are numerous cheating techniques that can't always be detected from a single player backup. As a result, it’s possible that **some cheaters may still be included**.


## 🤓 For the nerds

### How does this work?

Wasmegg send me the EIDs (of people who choose to join) via the [submitEID POST request](https://legendary-study-3-0.vercel.app/apidocs/#/default/post_submitEID). If a recent backup (within the last hour) isn't already available, the system fetches a fresh backup from the Auxbrain server, processes the data, and stores it in a MongoDB Cluster.

Every day, a GitHub Action triggers `calc_daily_reports.py`, which does queries to the cluster above and generate the report file, which is uploaded to another MongoDB Cluster.

### Swagger

I have created a [Swagger interface](https://legendary-study-3-0.vercel.app/apidocs/) for the API documentation. 


## 📙 Issues or suggestion
In case of issues or suggestion, open a [GitHub issue](https://github.com/Brosssh/legendary-study-3.0/issues/new?template=Blank+issue) or contact me on Discord (brosssh)
