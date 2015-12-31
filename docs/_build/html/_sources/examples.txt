Examples
========


Workflow for the client credentials grant type
----------------------------------------------

.. code-block:: python
    :linenos:

    #import library
    import deviantart

    #create new client
    da = deviantart.Api("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET");

    #define defaults
    deviations = []

    #the name of the user we want to fetch deviations from
    username = "ioneiy"

    offset = 0
    has_more = True

    #while there are more deviations to fetch
    while has_more:

        try:

            #fetch deviations from user
            fetched_deviations = da.get_gallery_folder(
                username=username,
                offset=offset
            )

            #add fetched deviations to stack
            deviations += fetched_deviations['results']

            #update offset
            offset = fetched_deviations['next_offset']

            #check if there are any deviations left that we can fetch (if yes => repeat)
            has_more = fetched_deviations['has_more']

        except deviantart.api.DeviantartError as e:
            #catch and print API exception and stop loop
            print e
            has_more = False

    #loop through every fetched deviation and print title and
    #author (most likely the previous defined) of the deviation
    for deviation in deviations:
        print "Deviaton title: {}".format(deviation.title)
        print "Deviation author: {}".format(deviation.author.username)


Workflow for the authorzation code grant type
----------------------------------------------

.. code-block:: python
    :linenos:

    #import library
    import deviantart

    #create new client with the authorization code grant type
    da = deviantart.Api(
        "YOUR_CLIENT_ID",
        "YOUR_CLIENT_SECRET",

        #must be the same as defined as in your application on DeviantArt
        redirect_uri="YOUR_REDIRECT_URI",

        standard_grant_type="authorization_code",

        #the scope you want to access (default => everything)
        scope="user"
    );

    #The authorization URI: redirect your users to this
    auth_uri = da.auth_uri

    print "Please authorize app: {}".format(auth_uri)

    #Enter the value of the code parameter, found in to which DeviantArt redirected to
    code = raw_input("Enter code:")

    #Try to authenticate with the given code
    try:
        da.auth(code=code)
    except deviantart.api.DeviantartError as e:
        print "Couldn't authorize user. Error: {}".format(e)

    #If authenticated and access_token present
    if da.access_token:

        print "The access token {}.".format(da.access_token)
        print "The refresh token {}.".format(da.refresh_token)

        #the User object of the authorized user
        user = da.get_user()

        print "The name of the authorized user is {}.".format(user.username)
