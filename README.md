# ✨ The Legendary Study ✨

This is the backend that collect EIDs from [Wasmegg](https://wasmegg-carpet.netlify.app/), process them and generate daily reports showing the legendary distribution over the playerbase. The reports are available on [Wasmegg Legendary Study](https://wasmegg-carpet.netlify.app/legendary-study/).  

## About EID security

I (Brosssh) can never see the EIDs that this application uses. Your clean EID will be only used to make API calls to the game server. After the API call, **your EID is [obfuscated and hashed](https://github.com/Brosssh/legendary-study-3.0/blob/main/backend/utility.py#L22) before being stored**. An hashed string cannot be reversed, but it can still be used to uniquely identify the same user.

## The cheaters issue

As we know, cheaters exists. **Cheaters that use well know technique have been exlcuded.** However, there are numerous way of cheating, and only a few of them can be detected from just a single player backup. For this reason, **it is possible** that (some) cheaters are included in the study.   

## 📙 Issues or requests
In case of issues or suggestion, open a [GitHub issue](https://github.com/Brosssh/legendary-study-3.0/issues/new?template=Blank+issue) or contact me on Discord (brosssh). 
