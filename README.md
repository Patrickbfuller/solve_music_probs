# solve_music_probs
Use data to make more informed music business decisions!



### Business Understanding 

Indepedent musical artists or any artist with out a data team may have trouble deciding which geographic regions to invest in. If they've got a fan base in one location, who's to say they may not be able to build a fan base somewhere else in the country? But where to start? It's a big country! To help narrow down the options, I suggest starting with locations where similar artists are playing. A region with fans of similar artists will likely be fertile ground for expansion. A model that recommends untapped locations where similar artists have fans, would help provide a starting point for artists to expand.

### Data Understanding

Potential features for gauging similarity of two artists may include, sonic features or genre. For this experiment I will gauge similarity by playlist co-presence. If two artists are appearing in the same playlists together they would be similar. For example: Out of all the playlists that ArtistA appears in, the more ArtistB appears in, the more similar is ArtistB.

For comparing locations, I will use the distance between their geographic coordinates. Because of the curvature of the geographic coordinates, the unique distance computation, known as 'Haversine' will be applied.

### Data Preparation

##### Data Acquisition
For this model I collected the playlists featured in each of the main spotify categories. These include varying concepts such as: 'Rock', 'KPop', 'Sessions', 'Party', 'Mood', 'Pride', etc. I intentionally excluded the categories, 'family', 'comedy', 'word', 'ellen', 'sleep', as the artists will be less correlated with musical concert data. The playlists and artists were collected using a python wrapper for the Spotify API called 'spotipy'. 
With this list of artitst, I also collected their concert locations from 'songkick.com'. To Account for granularity of location naming, I also collected the geographic coordinates for each unique concert location using the Google geocode API with the python package 'googlemaps'.

##### Data Cleaning
I collected the artists and playlists as appearances of artists in each playlist. This made it simple to one-hot encode the playlists. With a resulting flag for presence of the artists in their playlist, I then grouped the data by artist and aggregating the flags, resulting in a row for each artist with a boolean for  each playlist in which they appear. 
For the concerts: I removed any data points older than 2015, and any data for concerts outside of the US. I then merged the geographic coordinates to the concerts. Finally, to help prevent capitilzation errors, all the names of the artists in both tables were coerced to lowercase.

### Modeling


I'll set aside a final validation set of labeled images, maybe 20% for each class. Then I'll use Tensorflow to build an image classifier by fine tuning a pre-trained base model and tf.keras.Sequential. I'll also try using deep feature extraction on the images and making predictions using logistic regression, random forest, etc.

### Evaluation
I will report both the accuracy score and cross entropy loss, on training and test data. Because I don't want to die in the woods, I'll tie the evaluation back to my original business problem and choose classification thresholds that maximize recall for poisonous berries. I plan to use k-fold cross validation to do any needed parameter tuning.

### Deployment
The model will be deployed as a Flask app that can be used to upload a picture of a plant from a mobile phone to get a prediction of its species.


Business Understanding
Clear understanding of the problem and how you’re out to solve it.
Easy to see how the problem impacts you/your organization

Data Understanding
Gather data: is it feasible? Is there a plan for how to get the data? How to store it?
Describe every variable
Explore data
Verify quality

Data Preparation
Select data
Clean data
Construct data
Integrate data
Format data

Modeling
Select techniques
Design test(s)
Build model(s)
Assess model(s)

Evaluation
Evaluate results
Review the process
Determine the next steps
Review final results

Deployment
Plan deployment (your methods for integrating data mining discoveries into use)
Report final results
