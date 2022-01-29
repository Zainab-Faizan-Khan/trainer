
import cv2
from flask import Flask, render_template, Response,request,redirect,url_for,jsonify,session
from firebase_admin import credentials,firestore,initialize_app


import mediapipe as mp
import numpy as np



#storing sessional information for reps counter
class resulte():
    def __init__(self,count=0):
        self.count=count
        self.right=False
        self.left=False
    def setco(self,n):
        self.count=n
    def getco(self):
        return self.count



app = Flask(__name__)

app.secret_key="abc"
cred=credentials.Certificate('key.json')
default_app=initialize_app(cred)
db=firestore.client()

r=resulte()


#the root route

@app.route('/',methods=('GET','POST'))
def index0():

    return redirect("welcome")

@app.route('/home',methods=('GET','POST'))
def index6():
        
        return redirect("welcome")

#main page
@app.route('/welcome',methods=('GET','POST'))
def index():
    
    message=""
    session['signal']=None

    h='welcome'
    session['back']=h
    if(request.method=='POST'):
        if(request.form['email']==""):
            message="Email is required"
            return render_template('welcome.html',message=message)
        elif(request.form['code']==""):
            message="Code is required"
            return render_template('welcome.html',message=message)
        else:
            try:

                collect=db.collection('Logs').where('code','==',int(request.form['code']))
                col=collect.get()
                l=db.collection('Logs').where("code",'==',int(request.form['code'])).get()

                
                session['id']=l[0].id
                print(session['id'])

                if(col):
                    
                    res=[doc.to_dict() for doc in collect.stream()]
                    
                    email=res[0]['email']
                    if(email==request.form['email']):
                        session['excersise']=res[0]['title']
                        session['code']=res[0]['code']
                        session['reps']=res[0]['reps']
                        session['email']=email
                        r.setco(0)
                        return redirect('instructions')
                    else:
                        message="Invalid combination. No such appointment is found"
                        return render_template('welcome.html',message=message)

                else:
                    message="No such booking"
                    return render_template('welcome.html',message=message)


            except Exception as e:
                print(e)
            return redirect('instructions')
    return render_template('welcome.html')

#instructions page
@app.route('/instructions',methods=('GET','POST'))
def instruct():
    
        back=session['back']
        b=["Hold your camera in a position that your shoulder, elbows and wrists are visible.Click the start Button for your training.To change arms, click the right or left button placed at the bottom of the screen.The total reps are displayed at the bottom of the screen","The green flashes indicate the correct poses .Move your arm up to your shoulder until you make less than 10 degree between your shoulder elbow and wristand  the light flashes and move them down to 180 degree similarly.When youre done click the stop button"]
        l=["Hold your camera in a position that your shoulder, hips and wrists are visible.Click the start Button for your training .The total reps are displayed at the bottom of the screen","The green flashes indicate the correct poses .Move your arms up perpendicularly untilyou make 90 degree between elbow shoulder and hips and the light flashes and move your arms down to 0 degree similarly.When youre done click the stop button"]
        

        if(request.method=='POST'):
            back=session['back']
            print("i am here",back)
            if(back=='inst'):            
                if(session['excersise']=="Lateral Raise"):
                    return redirect('lateral')
                elif(session['excersise']=="Bicep Curl"):
                    return redirect('bicep')   
            else:
                return redirect("welcome")
        else:
            print("i am here",back)
            if(back=='welcome'):
                if(session['excersise']=="Lateral Raise"):
                    i1=l[0]
                    i2=l[1]
                    inst_img="../static/images/lateralextension.jpeg"
                    
                elif(session['excersise']=="Bicep Curl"):
                    i1=b[0]
                    i2=b[1]
                    inst_img="../static/images/bicepcurl.jpeg"
                back="inst"
                session['back']=back
                return render_template('instructions.html',excersise=session["excersise"],i1=i1,i2=i2,inst_img=inst_img)
            else:
                return redirect("welcome")



@app.route('/progress',methods=('GET','POST'))
def index2():
        k=session['back']
        if(k=="h"):
            session['back']="pro"
            ct=db.collection('users').where('email','==',str(session['email']))
            col=ct.get()
            
            if(col):
                res=[doc.to_dict() for doc in ct.stream()]
                print(res)

                print("the reps are",r.getco())
                session['reps']=r.getco()
                session['name']=res[0]['username']
                session['excersise']=session['excersise']
                session['one']=res[0]['one']
                return render_template('progress.html',e=session['excersise'],n=session['name'],r=session['reps'])
            else:
                print("the email is",session['email'])
                return render_template('progress.html')
        else:
            return redirect('welcome')


#save progress to the db

@app.route('/save',methods=('GET','POST'))
def s():
        k=session['back']
        if (k=="pro"):
            p=db.collection('users').where("email",'==',session['email']).get()
            session['back']=""
                    
            session['uid']=p[0].id
            
            q={'one':session['reps']}
            db.collection('users').document(session['uid']).update(q)

            s={'reps':session['reps']}
            db.collection('Logs').document(session['id']).update(s)
            return render_template('progress.html',m="Your progress has been saved",e=session['excersise'],n=session['name'],r=session['reps'])
        else:
            return redirect('welcome')

#switching between arms
@app.route('/right',methods=('GET','POST'))
def changearm1():
    
        session['arm']='Right Arm '
     
        return render_template('bicep.html',signal=session['signal'],arm=session['arm'])
    
@app.route('/left',methods=('GET','POST'))
def changearm():
     
            session['arm']='Left Arm '
      
            return render_template('bicep.html',signal=session['signal'],arm=session['arm'])


@app.route('/bicep',methods=('GET','POST'))
def index1():
        m=session['back']

        if(request.method=="GET"):
            if(m=='inst'):
                session['back']="h"
                session['signal']="Start"
                return render_template('bicep.html',signal=session['signal'])
            else:
                return redirect('welcome')
        else:
            if(m=='h'):
                if(session['signal']=="Start"):
                    session['signal']="Stop"
                    
                    session['arm']='Left Arm '
                    return render_template('bicep.html',signal=session['signal'],arm=session['arm'])
                elif(session['signal']=="Stop"):
                    
                    return redirect('progress')
            else:
                return redirect('welcome')
   



@app.route('/lateral',methods=('GET','POST'))
def index9():
        m=session['back']
        
        if(request.method=="GET"):
            if(m=='inst'):
                session['back']="h"
                session['signal']="Start"
                return render_template('lateralraise.html',signal=session['signal'])
            else:
                return redirect('welcome')
        else:
            if(m=='h'):
                if(session['signal']=="Start"):
                    session['signal']="Stop"
                    
                    return render_template('lateralraise.html',signal=session['signal'])
                elif(session['signal']=="Stop"):
                    
                    return redirect('progress')
            else:
                return redirect('welcome')

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return round(angle) 


def trackl():

    my_pose = mp.solutions.pose
    

    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    counter=r.getco()
    stage=None
    angle=0
    sx=0
    sy=0
    ex=0
    ey=0
    wx=0
    wy=0    
    
    with my_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            success, img = cap.read()
            
            # converting image to RGB from BGR cuz mediapipe only work on RGB
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB.flags.writeable=False
            results = pose.process(imgRGB)
            imgRGB.flags.writeable=True
            imgRGB = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)
            
            h,w,c=img.shape
            
            
            try:            
                landmarks = results.pose_landmarks.landmark
                    
                sx=landmarks[my_pose.PoseLandmark.LEFT_SHOULDER.value].x
                sy=landmarks[my_pose.PoseLandmark.LEFT_SHOULDER.value].y
                ex=landmarks[my_pose.PoseLandmark.LEFT_ELBOW.value].x
                ey=landmarks[my_pose.PoseLandmark.LEFT_ELBOW.value].y
                wx=landmarks[my_pose.PoseLandmark.LEFT_WRIST.value].x
                wy=landmarks[my_pose.PoseLandmark.LEFT_WRIST.value].y
                
                shoulder = [sx,sy]
                elbow = [ex,ey]
                wrist = [wx,wy]
                
                angle = calculate_angle(shoulder, elbow, wrist)
                
                if angle > 160:
                    stage = "down"
                
                if angle < 40 and stage =='down':
                    stage="up"
                    counter +=1
                    
                
                if (angle <40 or angle >160 ):
                    color=(0,255,0)
                else:
                    color=(0,0,255)  
                
                w1=wx*w
                w2=wy*h
                w3=ex*w
                w4=ey*h
                w5=sx*w
                w6=sy*h
                r.setco(counter)
                cv2.putText(img,str(counter), (300, 430), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.putText(img,str(angle), (189, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.line(img, (int(w5), int(w6)), (int(w3), int(w4)),color, 3)
                cv2.line(img, (int(w1), int(w2)), (int(w3), int(w4)),color, 3)
                cv2.circle(img, (w1, w2), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (w3, w4), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (w5, w6), 5, (178, 102, 255), cv2.FILLED)
                
        # print(angle, per)


                
            except:
                pass
            

              

           

            
            
            #cv2.imshow("Pose detection", img)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    
    cap.release()

def trackr():
    

    # creating our model to detected our pose
    my_pose = mp.solutions.pose
    

    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    counter=r.getco()
    stage=None
    angle=0
    sx=0
    sy=0
    ex=0
    ey=0
    wx=0
    wy=0
    
    with my_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            success, img = cap.read()
            
            # converting image to RGB from BGR cuz mediapipe only work on RGB
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB.flags.writeable=False
            results = pose.process(imgRGB)
            imgRGB.flags.writeable=True
            imgRGB = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)
            
            h,w,c=img.shape
            
            
            try:            
                landmarks = results.pose_landmarks.landmark
                    
                sx=landmarks[my_pose.PoseLandmark.RIGHT_SHOULDER.value].x
                sy=landmarks[my_pose.PoseLandmark.RIGHT_SHOULDER.value].y
                ex=landmarks[my_pose.PoseLandmark.RIGHT_ELBOW.value].x
                ey=landmarks[my_pose.PoseLandmark.RIGHT_ELBOW.value].y
                wx=landmarks[my_pose.PoseLandmark.RIGHT_WRIST.value].x
                wy=landmarks[my_pose.PoseLandmark.RIGHT_WRIST.value].y
                
                shoulder = [sx,sy]
                elbow = [ex,ey]
                wrist = [wx,wy]
                
                              
                angle = calculate_angle(shoulder, elbow, wrist)
                
                
                if angle > 160:
                    stage = "down"
                
                if angle < 40 and stage =='down':
                    stage="up"
                    counter +=1
                    
                
                if (angle <40 or angle >160 ):
                    color=(0,255,0)
                else:
                    color=(0,0,255)  
                
                w1=wx*w
                w2=wy*h
                w3=ex*w
                w4=ey*h
                w5=sx*w
                w6=sy*h
                r.setco(counter)
                cv2.putText(img,str(counter), (300, 430), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.putText(img,str(angle), (189, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.line(img, (int(w5), int(w6)), (int(w3), int(w4)),color, 3)
                cv2.line(img, (int(w1), int(w2)), (int(w3), int(w4)),color, 3)
                cv2.circle(img, (int(w1), int(w2)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(w3), int(w4)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(w5), int(w6)), 5, (178, 102, 255), cv2.FILLED)
                

                
            except:
                pass
            


            #cv2.imshow("Pose detection", img)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    
    cap.release()

def latraise():

    # creating our model to draw landmarks
    mp_drawing = mp.solutions.drawing_utils
    # creating our model to detected our pose
    my_pose = mp.solutions.pose
    

    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    counter=0
    stage=None
    angle1=0
    angle2=0
    
    with my_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, img = cap.read()
            
            # converting image to RGB from BGR cuz mediapipe only work on RGB
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB.flags.writeable=False
            results = pose.process(imgRGB)
            imgRGB.flags.writeable=True
            imgRGB = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)
            
            h,w,c=img.shape
            
            
            try:            
                landmarks = results.pose_landmarks.landmark
                    
                s1x=landmarks[my_pose.PoseLandmark.RIGHT_SHOULDER.value].x
                s1y=landmarks[my_pose.PoseLandmark.RIGHT_SHOULDER.value].y
                e1x=landmarks[my_pose.PoseLandmark.RIGHT_HIP.value].x
                e1y=landmarks[my_pose.PoseLandmark.RIGHT_HIP.value].y
                w1x=landmarks[my_pose.PoseLandmark.RIGHT_ELBOW.value].x
                w1y=landmarks[my_pose.PoseLandmark.RIGHT_ELBOW.value].y
                
                shoulder1 = [s1x,s1y]
                elbow1 = [w1x,w1y]
                hip1 = [e1x,e1y]
                              
                angle1 = calculate_angle(elbow1, shoulder1, hip1)

                    
                

                s2x=landmarks[my_pose.PoseLandmark.LEFT_SHOULDER.value].x
                s2y=landmarks[my_pose.PoseLandmark.LEFT_SHOULDER.value].y
                e2x=landmarks[my_pose.PoseLandmark.LEFT_HIP.value].x
                e2y=landmarks[my_pose.PoseLandmark.LEFT_HIP.value].y
                w2x=landmarks[my_pose.PoseLandmark.LEFT_ELBOW.value].x
                w2y=landmarks[my_pose.PoseLandmark.LEFT_ELBOW.value].y
                
                shoulder2 = [s2x,s2y]
                hip2 = [e2x,e2y]
                elbow2 = [w2x,w2y]
                
                angle2 = calculate_angle(elbow2, shoulder2, hip2)
                
                if angle1 < 20 and angle2 < 20:
                    stage = "down"
                
                if (angle1 > 75 and angle2 >75) and stage =='down' :
                    stage="up"
                    counter +=1
                    
                
                if (angle1 >75 and angle2 >75 ):
                    color=(0,255,0)
                elif ( angle1 <20 and angle2 < 20):
                    color=(0,255,0)
                else:
                    color=(0,0,255)                
                qt1=s1x*w
                qt2=s1y*h
                qt3=e1x*w
                qt4=e1y*h
                qt5=w1x*w
                qt6=w1y*h


                pt1=s2x*w
                pt2=s2y*h
                pt3=e2x*w
                pt4=e2y*h
                pt5=w2x*w
                pt6=w2y*h



               
                
                r.setco(counter)
                cv2.putText(img,str(counter), (300, 430), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.putText(img,str(angle1), (189, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5,(0,0,102) , 2)
                cv2.line(img, (int(qt1), int(qt2)), (int(qt3), int(qt4)),color, 3)
                cv2.line(img, (int(qt1), int(qt2)), (int(qt5), int(qt6)),color, 3)
                cv2.circle(img, (int(qt1), int(qt2)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(qt3), int(qt4)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(qt5), int(qt6)), 5, (178, 102, 255), cv2.FILLED)
                cv2.line(img, (int(pt1), int(pt2)), (int(pt3), int(pt4)),color, 3)
                cv2.line(img, (int(pt1), int(pt2)), (int(pt5), int(pt6)),color, 3)
                cv2.circle(img, (int(pt1), int(pt2)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(pt3), int(pt4)), 5, (178, 102, 255), cv2.FILLED)
                cv2.circle(img, (int(pt5), int(pt6)), 5, (178, 102, 255), cv2.FILLED)                
                

                
            except:
                pass

            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    
    cap.release()




#for the simple screen before starting of excersise

def show():
    my_pose = mp.solutions.pose
    

    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    with my_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, img = cap.read()
            
            # converting image to RGB from BGR cuz mediapipe only work on RGB
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB.flags.writeable=False
            results = pose.process(imgRGB)
            imgRGB.flags.writeable=True
            imgRGB = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    cap.release()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if(session['signal']=="Stop"):
        if(session['arm']=='Left Arm '):
            return Response(trackl(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return Response(trackr(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')            
    else:

        return Response(show(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/videofeedforlatraise')
def videofeedforlatraise():
    if(session['signal']=="Stop"):
        return Response(latraise(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    else:

        return Response(show(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)







