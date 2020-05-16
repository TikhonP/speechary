from multiprocessing.pool import ThreadPool
#from genderize import Genderize
#from transliterate import translit, get_available_language_codes
from PIL import Image
import numpy as np
import requests
import time
import random
import traceback
import cv2
import multiprocessing as mp

import ast
import json
from io import BytesIO
from deepface.basemodels import OpenFace
from face_recognition import face_recognition
from threading import Thread
from deepface.extendedmodels import Gender, Race
from deepface import DeepFace
from keras.preprocessing import image
import warnings
from deepface.commons import functions, realtime, distance as dst
from deepface.commons import functions


sharedmemory = {}


def cnvt_broken_json(s):
    s = s.replace('\\', '').replace("'", '"')
    # print(s)
    startphotos = ', "photo_urls": ['
    endphotos = '], "caption": ['
    startavatar = ', "avatar": "'
    endavatar = '", "full_name": "'
    usrstart = ', "username": "'
    usrend = '", "last_post_at": '
    laststart = '", "last_post_at": '
    lastend = ', "photo_urls": ["'
    av = s.find(startavatar)
    fname = s.find(endavatar)
    urlss = s.find(startphotos)
    caption = s.find(endphotos)
    usrfind1 = s.find(usrstart)
    usrfind2 = s.find(usrend)
    laststartind = s.find(laststart)
    lastendind = s.find(lastend)
    urlist = s[(urlss+len(startphotos)-1):caption+1]
    avatar = s[(av+len(startavatar)):fname]
    photo_urls = ast.literal_eval(urlist)
    last_post_at = s[(laststartind + len(laststart)):lastendind]
    # print(last_post_at)
    username = s[(usrfind1+len(usrstart)):usrfind2]
    retjson = {'avatar': avatar, 'username': username, 'photo_urls': photo_urls,
               'username': username, 'last_post_at': int(last_post_at)}
    return retjson


def get_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert('RGB')


def get_user(ind):
    rightpath = 'parsedaccs/' + os.listdir('parsedaccs')[ind]
    with open(rightpath, 'r') as read_file:
        data = json.load(read_file)
    return data


def display(img):
    img.show()


def get_faces(img):
    face_landmarks_list = face_recognition.face_locations(np.array(img))
    faces = []
    for face in face_landmarks_list:
        faces.append(img.crop((face[3], face[0], face[1], face[2])))
    return faces


def add_toallfaces(link, rkey, val):
    global sharedmemory
    try:
        img = get_image(link)
        sharedmemory[rkey].extend([[f, val] for f in get_faces(img)])
    except:
        pass


def getfacesfromphotolist(photolist):
    avatartranslate = {True: 3, False: 1}
    faces = []
    faceweight = 0
    for photo in photolist:
        toextend = []
        for face in get_faces(photo[0]):
            faceweight += avatartranslate[photo[1]]
            toextend.append([face, avatartranslate[photo[1]]])
        faces.extend(toextend)
    return faces, faceweight


def add_toshared(link, rkey, isavatar):
    global sharedmemory
    try:
        img = get_image(link)
        sharedmemory[rkey].append([img, isavatar])
    except:
        pass


def get_all_faces(num):
    global sharedmemory
    user = cnvt_broken_json(allusers[num])
    randkey = random.randint(0, 10000)
    sharedmemory[randkey] = []
    allthr = []
    if 'avatar' in user:
        try:
            avthr = Thread(target=add_toallfaces, args=(
                user['avatar'], randkey, 3, ))
            avthr.start()
            allthr.append(avthr)
        except:
            pass
    for photo_url in user['photo_urls'][:10]:
        try:
            thr = Thread(target=add_toallfaces, args=(photo_url, randkey, 1, ))
            thr.start()
            allthr.append(thr)
        except:
            pass
    for th in allthr:
        th.join()
    all_faces = sharedmemory[randkey]
    del sharedmemory[randkey]
    return all_faces


def get_encodings(faces, openmodel):
    encodings = []
    normfaces = []
    input_shape = openmodel.layers[0].input_shape[1:3]
    for face in faces:
        try:
            if (face[0].size[0] * face[0].size[1]) > minimgsize:
                preface = preprocess_face(
                    np.array(face[0]), target_size=input_shape)
                vec_repres = openmodel.predict(preface)[0, :]
                encodings.append([vec_repres, face[1]])
                normfaces.append(face)
        except:
            traceback.print_exc()
    return encodings, normfaces


def how_many_face(face_enc, face_encodings):
    return face_recognition.compare_faces(face_encodings, face_enc)


def count_faces(encodings, counter):
    chosen = encodings[0]
    del encodings[0]
    counter[chosen[1]] = []
    if len(encodings) > 0:
        res = how_many_face(chosen[0][0], [enc[0][0] for enc in encodings])
        shift = 0
        score = []
        for i in range(len(encodings)):
            if res[i]:
                score.append(encodings[i-shift][1])
                del encodings[i - shift]
                shift += 1
        counter[chosen[1]] = score
        if len(encodings) > 0:
            return count_faces(encodings, counter)
        else:
            return counter
    else:
        return counter


def count_openfaces(vec_faces, counter):
    chosen = vec_faces[0]
    del vec_faces[0]
    counter[chosen[1]] = []
    if len(vec_faces) > 0:
        res = how_many_openface(chosen[0][0], [f[0][0] for f in vec_faces])
        shift = 0
        score = []
        for i in range(len(vec_faces)):
            if res[i]:
                score.append(vec_faces[i-shift])
                del vec_faces[i - shift]
                shift += 1
        counter[chosen[1]] = score
        if len(vec_faces) > 0:
            return count_openfaces(vec_faces, counter)
        else:
            return counter
    else:
        return counter


def frequent_face(counter):
    face_indxs = list(counter.keys())
    maximum = 0
    freq_face = face_indxs[0]
    for ind in face_indxs:
        coef = sum([k[0][1] for k in counter[ind]])
        if coef > maximum:
            maximum = coef
            freq_face = ind
    return freq_face


def indexize(array):
    return [[a, ind] for ind, a in enumerate(array)]


def show_photos(photos):
    for photo in photos:
        Thread(target=display, args=(photo, )).start()


def preprocess_face(face, target_size=(224, 224), gray_scale=False):
    if gray_scale:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(face, target_size)
    img_pixels = image.img_to_array(img)
    img_pixels = np.expand_dims(img_pixels, axis=0)
    img_pixels /= 255
    return img_pixels


def get_gender(prep_img, blob, model1, model2):
    model1.setInput(blob)
    gender_preds2 = model1.forward()
    gender_prediction = model2.predict(prep_img)
    mean = (gender_preds2[0][::-1] + gender_prediction) / 2
    return gender_list[np.argmax(mean[0])]
    # return np.argmax(gender_prediction)


def get_age(blob, model):
    model.setInput(blob)
    age_preds = model.forward()
    age2 = age_list[age_preds[0].argmax()]
    return age2


def get_race(prep_img, model):
    race_predictions = model.predict(prep_img)[0, :]
    return race_labels[np.argmax(race_predictions)]


def compare_imgs(img1, img2, openmodel):
    input_shape = openmodel.layers[0].input_shape[1:3]
    threshold = functions.findThreshold('OpenFace', 'cosine')
    img1c = preprocess_face(img1, target_size=input_shape)
    img2c = preprocess_face(img2, target_size=input_shape)
    img1_representation = openmodel.predict(img1c)[0, :]
    img2_representation = openmodel.predict(img2c)[0, :]
    distance = dst.findCosineDistance(img1_representation, img2_representation)
    if distance <= threshold:
        return True
    else:
        return False


def compare_vecimgs(vec1, vec2):
    distance = dst.findCosineDistance(vec1, vec2)
    if distance <= threshold:
        return True
    else:
        return False


def how_many_openface(vec_face, tocompare):
    return [compare_vecimgs(f, vec_face) for f in tocompare]


def get_gender_multiple(preprfaces, model):
    sumvec = np.array([0.0, 0.0])
    for fc in preprfaces:
        prd = model.predict(fc)[0]
        sumvec += prd
    meanvec = sumvec / len(preprfaces)
    return gender_list[np.argmax(meanvec)]


def show_all_faces(faces):
    for face in faces:
        # print(face)
        face[0].show()


def centroid_face(encodings):
    encodings = encodings
    encodings[0][1] -= 1
    centervec = encodings[0][0]
    allcount = 1
    for enc in encodings:
        for c in range(enc[1]):
            allcount += 1
            centervec += enc[0]
    centervec = centervec / allcount
    minndist = float('inf')
    minnind = 0
    for ind in range(len(encodings)):
        dist = dst.findCosineDistance(centervec, encodings[ind][0])
        if dist < minndist:
            minndist = dist
            minnind = ind
    # print(minndist)
    return minnind


def acc_analyzer(acc_json, models):
    try:
        gender_model, race_model, OpenFacemodel = models
        starttime = time.time()
        user = acc_json
        faces, faceweight = getfacesfromphotolist(user['all_photos'])
        if faceweight >= 3:
            print(user['username'], 'is private')
        else:
            print(user['username'], 'is говно')
        enc, nfaces = get_encodings(faces, OpenFacemodel)
        if enc and 'username' in user:
            center_face = centroid_face(enc)
            facearr = np.array(nfaces[center_face][0])
            img_224 = preprocess_face(
                facearr, target_size=(224, 224), gray_scale=False)
            gender_prediction = get_gender_multiple([img_224], gender_model)
            race_predictions = get_race(img_224, race_model)
            print(gender_prediction, race_predictions,
                  user['username'], time.time() - starttime)
    except Exception:
        traceback.print_exc()


def process_manager(q):
    gender_model = Gender.loadModel()
    print('gender_models done')
    race_model = Race.loadModel()
    print('race_models done')
    OpenFacemodel = OpenFace.loadModel()
    print('OpenFacemodels done')

    for typemodel in [gender_model, race_model, OpenFacemodel]:
        typemodel._make_predict_function()

    while True:
        acc_json = q.get()
        acc_analyzer(acc_json, [gender_model, race_model, OpenFacemodel])


def parse_addtoque(userjson, q):
    global sharedmemory
    user = cnvt_broken_json(userjson)
    randkey = random.randint(0, 10000)
    sharedmemory[randkey] = []
    allthr = []
    if 'avatar' in user:
        try:
            avthr = Thread(target=add_toshared, args=(
                user['avatar'], randkey, True,))
            avthr.start()
            allthr.append(avthr)
        except:
            pass
    for photo_url in user['photo_urls'][:10]:
        try:
            thr = Thread(target=add_toshared, args=(
                photo_url, randkey, False,))
            thr.start()
            allthr.append(thr)
        except:
            pass
    for th in allthr:
        th.join()
    all_photos = sharedmemory[randkey]
    del sharedmemory[randkey]
    user['all_photos'] = all_photos
    q.put(user)


allusers = open(
    'C:/Users/User/PycharmProjects/InstAccClassify/100kparsed3.txt').read().split('\n')
minimgsize = 32 ** 2
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
age_list = ['0-2 years', '4-6 years', '8-12 years', '15-20 years',
            '25-32 years', '38-43 years', '48-53 years', '60-100 years']
gender_list = ['Female', 'Male']
race_labels = ['asian', 'indian', 'black',
               'white', 'middle eastern', 'latino hispanic']
threshold = functions.findThreshold('OpenFace', 'cosine')
if __name__ == '__main__':
    mp.set_start_method('spawn')
    q = mp.Queue()
    processes = [mp.Process(target=process_manager, args=(q, ))
                 for _ in range(4)]
    for process in processes:
        process.start()
        time.sleep(10)
    for user in allusers[:100]:
        Thread(target=parse_addtoque, args=(user, q, )).start()
        time.sleep(0.1)
    for process in processes:
        process.join()
