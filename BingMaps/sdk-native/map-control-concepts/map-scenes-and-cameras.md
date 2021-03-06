
## Scenes and Cameras

Because the Map View can show both oblique and nadir views, as well as 3D topology, it is important to carefully set your view so that
obstacles, such as mountains, do not get in your way.  
To help with this, the Bing Maps Native control supports a concept of "scenes" as a
primary tool for establishing a view.  
Via the [MapScene](../map-control-api/MapScene-class.md) static methods, you can establish different perspectives and the map will automatically choose the best "camera" for that perspective based on environmental factors, including the user's current view within the map.

### Examples

#### Set the initial location of a map 

The following example shows how to set the starting location of an map using `setScene`. This sets map to be zoomed in over London, UK on start up.

**Swift**

> ```swift
> override func viewDidLoad() {
>     super.viewDidLoad()
> 
>     mapView.credentialsKey = "credentials here"
>     let scene = MSMapScene(location: MSGeolocation(latitude: 51.50632, -0.12714), zoomLevel: 10))
>     self.mapView.setScene(scene, with: .none)
> }
> ```

#### Handle completion after the camera arrives

The following example shows  how to move the camera to Seattle with default animation and handle animation complete.

**Swift**

> ``` swift
>     // Set map to seattle asynchronously
>     func setMapToSeattle() {
>         // Specify a known location.
>         let cityPosition = MSGeolocation(latitude:47.604, longitude:-122.329)
>         let scene = MSMapScene(location: cityPosition, zoomLevel: 12)
>         mapView.businessLandmarksVisible = true
> 
>         // Set the map location and
>         mapView.beginSetScene(scene, with: .default, withCompletionCallback: {_ in
>             // add code here to run scenario after the camera arrives at your destination
>         })
>     }
> ```

#### Show the location and a radius of 1000 meters around the location. Animate to it with a linear style animation

**Java**

>```java
> mMap.setScene(MapScene.ofLocationAndRadius(new Geolocation(47.599025, -122.339901), 1000), MapAnimationKind.LINEAR);
>```
>

**Swift**

>``` swift
> let scene = MSMapScene(location: MSGeolocation(latitude:47.599025, longitude:-122.339901), radius:1000);
> mapView.setScene(scene, with: .linear)
> ```

**Objective-C**

>``` objectivec
> MSMapScene *scene = [MSMapScene sceneWithLocation:[MSGeolocation geolocationWithLatitude:47.599025 longitude:-122.339901]
>                                           radius:1000];
> [self.mMap setScene:scene withAnimationKind:MSMapAnimationKindLinear]
>```

#### Show an area on the screen

**Java**

>```java
>GeoboundingBox seattle = new GeoboundingBox(new Geolocation(47.599025, -122.339901), new Geolocation(47.589908, -122.313251));
>mMap.setScene(MapScene.ofBoundingBox(seattle), MapAnimationKind.LINEAR);
>```

**Swift**

>``` swift
> let seattle = MSGeoboundingBox(northwest: MSGeolocation(latitude:47.599025, longitude:-122.339901),
>                                   southeast: MSGeolocation(latitude:47.589908, longitude:-122.313251))
> let scene = MSMapScene(boundingBox: seattle)
> mapView.setScene(scene, with: .linear)
> ```


**Objective-C**

>``` objectivec
>MSGeoboundingBox *seattle =
>    [[MSGeoboundingBox alloc] initWithNorthwest:[MSGeolocation geolocationWithLatitude:47.599025 longitude:-122.339901]
>                                         southeast:[MSGeolocation geolocationWithLatitude:47.589908 longitude:-122.313251]];
>MSMapScene *scene = [MSMapScene sceneWithBoundingBox:seattle];
>[self.mMap setScene:scene withAnimationKind:MSMapAnimationKindLinear];
>```

_See also_
[MapScene](../map-control-api/MapScene-class.md)
