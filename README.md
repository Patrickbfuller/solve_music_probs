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
To model artist similarity, an unsupervised NearestNeighbor model is fit to the artists' playlist appearances and evaluate their distance with cosine similarity in the multiple dimensions(1763 different playlists).

Next for a given featured artist, a second NearestNeighbor trains on the locations that an artist has played. Then, iterating through each place that a simlilar artist has played but the featured artist has not, this second NearestNeighbor finds the nearest location that the featured artist HAS played. A custom class returns these new locations ordered by distance from a the locations already played. The distance between locations is computed with the haversine calculation to account for the irregularity of longitudinal distance.

### Evaluation
I do not currently have a metric for evaluating the results of these models. 

The reported similar artists seem to be relevant, but should be taken with a grain of salt. Sometimes there are multiple artists with cosine distances in the range of 0.6-0.7 that may be a reasonable assumption for having a similar fan base. Sometimes the only relevant artists have a distance of 0.4 or 0.5 and 'farther' aritsts are not so similar. 

The reported potential new locations commonly report cities in Florida, or New Mexico, or Colorado. This is due to Florida being a peninsula and the sparcity of cities in the desert and mountain regions.

### Deployment
I hope to deploy this to a flask app but since my model is not predicting on any new input I am unsure whether an input box is appropriate.