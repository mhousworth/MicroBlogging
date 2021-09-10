#!/usr/bin/env python3

# Microblogging - Message Database Initial Schema Script

import requests


def generate_posts():

    # Sample Authentication from users database
    joeAuth = ('Joe','Clone3')
    raulAuth = ('Raul','2Raptor4')
    benAuth = ('Ben','Fum6le')

    dt = {'username':'Joe', 'text':'Hello World'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'How many programmers does it take to change a light bulb? None, thats a hardware problem'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'Whats the object-oriented way to become wealthy? Inheritance'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'Why did the programmer quit his job? Because he didnt get arrays'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'What did the Java code say to the C code? Youve got no class'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'Why are Assembly programmers always soaking wet? They work below C-level'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'What is the most used language in programming? Profanity'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'Why did the database administrator leave his wife? She had one-to-many relationships'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'Why do programmers always get Christmas and Halloween mixed up? Because DEC 25 = OCT 31'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)
    dt = {'username':'Joe', 'text':'How did the programmer die in the shower? He read the shampoo bottle instructions: Lather. Rinse. Repeat.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=joeAuth)

    
    dt = {'username':'Raul', 'text':'If you cant handle the story thats ok'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'This story is the devs explaining how they had to nuke the game to remake it from scratch'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'Gonna put a saddle on ratsqueak and see how that bad boy can fly'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'I can throw them around like a football'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'This also doesnt matter'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'If Im not back in time remember...'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'lancallium'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'Egg'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'I saved the image before I could realize what I was doing'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)
    dt = {'username':'Raul', 'text':'Throw bodies at the problem for science'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=raulAuth)


    dt = {'username':'Ben', 'text':'Im not saying there shouldnt be A system, rather that the current one sucks and doesnt work'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'I would personally prefer a system where you pay into an account you dont have access to until you either pay off the loan, or else sell the thing in question.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'That way that extra interest isnt getting eaten up by the bank and you still get it back, only if you pay the loan back tho.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'That way you have both the bank having something to fall back on if they default, and the end user doesnt get screwed.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'Not interest free, but instead of the interest hike going to bank profit, it goes into a fund that only gets payed back if they complete the loan.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'So that way, from the banks profit perspective, everyone has the same rate, but from a risk perspective, the higher risk people pay more.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'This way they cant profit off of higher risk people, but still have that money to inevitably fall back on if they cant pay.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'And hey, if the high risk people do complete it, its as if they were low risk.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'Only if they completely pay back the loan'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'If they fail to, it goes to the bank'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)
    dt = {'username':'Ben', 'text':'More of a hypothetical account rather than a literal bank account.'}
    r = requests.post(url = 'http://localhost:5000/posts/', json=dt, auth=benAuth)


if __name__ == '__main__':
    generate_posts()