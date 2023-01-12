#-----------------------------------------------------------------------------
# Name:        Discord Cyberbullying Bot
# Purpose:     To provide a streamlined process removing cyberbullying from
#              discord using a variety of techniques
#
# Author:      FAIZAN SHAIKH,AYUSH SINHA,TANAY SHENOY,ESHAN OZARKAR
# Created:     24-OCTOBER-2022
#-----------------------------------------------------------------------------

from serverSetup import *
from client.imports import * # client imports
from server.imports import * # server imports
from better_profanity import profanity
import discord

print("Starting up...") # Notify file was run


@client.event
async def on_ready():
    '''
    Asynchronous function that runs when bot is ready, changes status, and prints message
    Reference: https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    '''
    await client.change_presence(activity=discord.Game(name='Imma flag some people'))
    print("Bot is online")

admin_channel = -1
reporting_channel = -1

@client.event
async def on_reaction_add(reaction, user):
 if user!=BOTID:    
    if reaction.emoji == '\U0001F44D':

     # Delete Message
     await G_message.delete()

     # Train Classifier
     # classifiers.qClassifier_train(G_message.content,'neg')
     await G_message.channel.send("Data Updated(neg)")
                
    elif reaction.emoji == '\U0001F44E':
        
     # Train Classifier
     # classifiers.qClassifier_train(G_message.contentt,'pos')
     await G_message.channel.send("Data Updated(pos)")

  
async def EMBED(id,confidence,content,channel):
    embed = discord.Embed(
			title='REPORTING USER',
			description='THIS USER USED PROFANITY',
			colour=discord.Colour.red()
			)
    embed.add_field(name="MESSAGE CONTENT",value=content,inline=False)
    embed.add_field(name="USER ID",value=id,inline=True)
    embed.add_field(name="CONFIDENCE LEVEL",value=confidence,inline=True)
    await channel.send(embed=embed)
    
@client.event
async def on_message(message):
    
    '''
    Welcome to the Cyberbullying Detection and Assistance Tool. If you just got started, type `!setup` to initialize the server.

    Commands
    --------
    `!setup`: creates necessary channels, roles, and 
    `!add [str]`: adds the string to the list of bad words
    `!delete [str]`: deletes the string from the list of bad words
    `!print`: sends out the current bad words
    `!names`: list out all users who have sent at least 1 message
    `!swears`: list out swears for all users
    `!swears [user object]`: list out swears for that user
    `!report [message id]`: reports a message
    `!roleAdd [user] [role]`: adds a role to the user
    `!roleDelete [user] [role]`: deletes a role from the user
    `!help`: displays this message
    '''

    global baddiesList
    global users
    global admin_channel
    global users, userIDs
    global G_message
    
    G_message= message
    
    '''
    Update database if it's a new user
    '''
    
    if str(message.author.id) not in userIDs:
        if "Seidelion" in [y.name for y in message.author.roles]:
            newUser = seidelions.Seidelion(str(message.author.id),str(message.author),userDatabase,0,"Seidelion",0)
        else:
            newUser = user.User(str(message.author.id),str(message.author),userDatabase,0,"User")
        users.append(newUser)
        userIDs.append(str(message.author.id))
        newUser.insert()

    '''
    Predefine commonly used values to increase reusability
    '''
    inputText = message.content # Text of the message
    currentUser = users[userIDs.index(str(message.author.id))] # The current user typing
    mentionedUser_index = -1 # The index of the user mentioned
    if len(message.mentions) > 0:

        def binarySearch(idList,idToFind): 
            '''Binary Search to get index of mentioned user in the "users" array
            
            Parameters
            ----------
            idList: int[]
                the list of ids
            
            idToFind: int
                the id to be found

            Returns
            -------
            int:
                the index of the mentioned user
                -1 if not found
            '''

            first = 0
            last = len(idList) - 1
            while first <= last: 
        
                mid = (first+last)//2

                if idList[mid] == idToFind: 
                    return mid 
        
                elif idList[mid] < idToFind: 
                    first = mid + 1
        
                else:
                    last = mid - 1

            return -1

        mentionedUser_index = binarySearch(userIDs,message.mentions[0].id)

    admin_channel, reporting_channel = -1, -1
    for channel in message.guild.channels:
        if channel.name == "administration":
            admin_channel = discord.Object(id=channel.id)
           
        if channel.name == "reporting":
            reporting_channel = discord.Object(id=channel.id)
           

    hasNoChannel = admin_channel == -1 or reporting_channel == -1
    isCommand = inputText.startswith("!") and not inputText == "!setup"
    if hasNoChannel and isCommand:
        await message.channel.send('The channels "administration" and/or "reporting" are not found. Please initialize setup by typing `!setup` {0.name}'.format(message.author))
    '''
    Administrative Functions
    '''

    if inputText.startswith("!setup"):
        if hasNoChannel:
            # try:
                # Reusable Components
                server = message.guild
                everyone = discord.PermissionOverwrite(read_messages=False, send_messages=False)
                mine = discord.PermissionOverwrite(read_messages=True)

                # Create Seidelion Role
                # role = await server.create_role(name='Seidelion', colour=discord.Colour(0x0FF4C6))
                # await client.add_roles(message.author, role)

                # Create Administration Channel
                await server.create_text_channel('administration')
                overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                rolesearch = discord.utils.get(server.roles, name="Seidelion")
                # await message.channel.set_permissions(message.channel.author, rolesearch, overwrite)
                await message.channel.set_permissions(message.author, read_messages=True,send_messages=True)
                await message.channel.send( "The 'administration' channel has been added!")

                # Creating Reporting Channel
                await server.create_text_channel('reporting')
                overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                rolesearch = discord.utils.get(server.roles, name="Seidelion")
                 #await message.channel.set_permissions(message.channel.author, rolesearch, overwrite)
                await message.channel.set_permissions(message.author, read_messages=True,send_messages=True)
                await message.channel.send( "The 'reporting' channel has been added!")

                # Add Role to Admin
                currentUser.updateRole("Seidelion")
                role="Seidelion"

                # Update User Database for Admin
                currentUser = seidelions.Seidelion(currentUser.id,currentUser.name,userDatabase,currentUser.swearCount,"Seidelion",0)
                await message.channel.send( "Successfully assigned role %s to %s" % (role, message.author))

               # Update User Database for Mr Seidel
                tempUserObject = users[userIDs.index(str(BOTID))]
                tempUserObject.updateRole("Seidelion")
                users[mentionedUser_index] = seidelions.Seidelion(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"Seidelion",0)
                await message.channel.send( "Successfully assigned role 'Seidelion' to self")

                # Initialize custom classifier
                classifiers.qClassifier_init()
                await message.channel.send( "Successfully created and reset custom classifier")
            # except Exception as e:
            #     print(e)
            #     await message.channel.send_message( "Oh no! Something went horrendously wrong.")
        else:
            
            await message.channel.send("Server is already set up")
    
    elif inputText == "!help":
        await message.channel.send( on_message.__doc__)
    
    if inputText.startswith("!restore"):
       baddiesList=wordFilter.fetch()
       await message.channel.send( "Bad words List Successfully Stored!!")
       
      
    
    '''
    Functions relating to users
    '''
    if inputText.startswith("!names"):
        for u in users:
            await message.channel.send(u.display())

    # Add / Remove roles
    if inputText.startswith("!role"):
        isCorrectFormat = inputText.count(' ') == 2 and len(message.mentions) == 1
        isRealRole = inputText.split()[2] in [y.name for y in message.guild.roles]
        hasPermissions = currentUser.perms == "Seidelion"

        # Add Roles
        if message.mentions[0].id == BOTID:
            await message.channel.send("Sorry, but you can't edit a bot's roles.")

        elif inputText.startswith("!roleAdd") and isCorrectFormat and isRealRole and hasPermissions:
            tempUser = message.guild.get_member(message.mentions[0].id)
            role = message.guild.roles[([y.name for y in message.guild.roles].index(inputText.split()[2]))]
            try:
                await client.add_roles(tempUser, role)
                await message.channel.send("Successfully assigned role %s to %s" % (role, tempUser))

                if inputText.split()[2] == "Seidelion":
                    tempUserObject = users[mentionedUser_index]
                    tempUserObject.updateRole("Seidelion")

                    users[mentionedUser_index] = seidelions.Seidelion(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"Seidelion",0)
            except Exception as e:
                print(e)
                await message.channel.send( "Oh No! Something went wrong!")

        # Remove Role
        elif inputText.startswith("!roleRemove") and isCorrectFormat and isRealRole and hasPermissions:
            tempUser = message.guild.get_member(message.mentions[0].id)
            role = message.guild.roles[([y.name for y in message.guild.roles].index(inputText.split()[2]))]
            try:
                await client.remove_roles(tempUser, role)
                await message.channel.send( "Successfully removed role %s from %s" % (role, tempUser))

                if inputText.split()[2] == "Seidelion":
                    tempUserObject = users[mentionedUser_index]
                    tempUserObject.updateRole("User")
                    users[mentionedUser_index] = user.User(tempUserObject.id,tempUserObject.name,userDatabase,tempUserObject.swearCount,"User")
            except Exception as e:
                print(e)
                await message.channel.send( "Oh No! Something went wrong!")

        if not hasPermissions:
            await message.channel.send( "You don't have the permissions to do that!")
        if not isCorrectFormat:
            await message.channel.send( "There's a problem with your input. Please make sure it's `!roleAdd/roleRemove @user rolename`")
        if not isRealRole:
                await message.channel.send( "That's not a real role!")

    elif inputText.startswith("!swears"):

        if len(message.mentions) == 0:
            def quickSort(usersArr):
                '''Recursive quicksort to sort the users by swears
                
                Paramters
                ---------
                usersArr: users[]
                    the user array
                
                Returns:
                    users[]: a sorted user array
                '''

                if len(usersArr)==0: return []
                if len(usersArr)==1: return usersArr
                left = [i for i in usersArr[1:] if i.swearCount > usersArr[0].swearCount]
                right = [i for i in usersArr[1:] if i.swearCount <= usersArr[0].swearCount]
                return quickSort(left)+[usersArr[0]]+quickSort(right)

            users = quickSort(users)
            for u in users:
                if u.swearCount > 0:
                 await message.channel.send( "Swear Count for %s - %s" % (u.name,u.swearCount))

        else:
            try:
                mentionedUser = users[mentionedUser_index]
                await message.channel.send( mentionedUser.swearCount)
            except ValueError as e:
                print(e)
                await message.channel.send("This user does not exist")
    
    '''
    Functions relating to Cyberbullying Reporting
    '''

    # Prints the bad word list
    if inputText.startswith("!print"):
        await message.channel.send(wordFilter.printAll())
   
    if ("!restore"):
        baddiesList=wordFilter.fetch()
        

    if inputText.startswith("!add ") and inputText.count(' ') > 0:
                  mes = inputText.split()[1]
                  if mes in baddiesList:
                     await message.channel.send( "Word already added")
                  else:
                     wordFilter.insert(mes,baddiesList) # Run and get status
                     await message.channel.send( "Successfully added %s to database" % mes)
                     baddiesList.append(mes)


        # Remove Bad Words
    elif inputText.startswith("!delete") and inputText.count(' ') > 0:
             mes = inputText.split()[1]

             if mes in baddiesList:
                  wordFilter.delete(mes)
                  await message.channel.send( "Successfully deleted %s from database" % mes)
                  baddiesList = wordFilter.fetch()
             else:
                 await message.channel.send( "You silly. %s is not even a banned word!" % mes)

             # Print Bad Words
    elif inputText.startswith("!print"):
                await message.channel.send(wordFilter.printAll())
    
    # Checks and classifiers messages
    if message.author != client.user: 
 
        cyberbullying_confidence = classifiers.isCyberbullying(inputText,baddiesList)
        
        if cyberbullying_confidence > 0 or profanity.contains_profanity(inputText):
            if cyberbullying_confidence == 0:
                classifiers.qClassifier_train(inputText,'neg')
            currentUser.updateSwears()
            await message.delete()
            await message.channel.send("Hey! Don't be such a downer!")
            channel = client.get_channel(reporting_channel.id)
            #await channel.send("!report {0} for saying '{1}' ".format(message.author.id, message.content))
            #await channel.send("Confidence: %s %%" % cyberbullying_confidence)
            await EMBED(message.author.id,cyberbullying_confidence,message.content,channel)
      
# Run the Bot
client.run(TOKEN)