# www2017petitions
"Predicting the Success of Online Petitions Leveraging Multidimensional Time-Series" WWW'17, Perth, Australia

dataSample.json - contains a sample of the 200 e-petitions as {PetitionId : {values}}.
Each petition has the following fields:
'last\_signers\_local\_time' - timestamps of the signatures in the PST timezone,
'goal' - goal number of signatures for the petition,
'title' - title of the petition,
'front\_page' - time series of the ranking of the petition on the front page (if available). It has the following format: [[timestamp, ranking],...],
'signers' - stores the number of signers of the petition,
'tweet\_time' - timestamps of the corresponding tweets in UTC,
'owner' - owner of the petition,
'petition\_id' - petition id,
'tweets' - more detailed information for each tweet that mention the petition (number of followers of the user, tweet id etc)
'utc\_aligned\_times' - timestamps of the signatures in UTC (thus comparable with the tweets timestamps),
'target' - target of the petition.

Folder Fit\_RateModel-Ext contains the code for the CRD model from the paper.
Input of the script:
  samp.txt in the following format:
    Data Length   Posted time
    Time          #Signatures
    ....
Output of the script:
  par.txr with the corresponding parameters of the model:
     a\_s   b\_s  phi\_0  k tau  Err
To run the code - following commands should be run:
make Fit\_sig
./fit\_sig  samp.txt par.txt
