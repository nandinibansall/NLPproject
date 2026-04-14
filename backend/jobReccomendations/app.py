import zipfile
zip_ref=zipfile.ZipFile("/content/archive (1).zip")
zip_ref.extractall("/content")
zip_ref.close()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
df=pd.read_csv("/content/UpdatedResumeDataSet.csv")
import re
def clean(txt):
  cleanedText=re.sub('https\S+',' ',txt)
  cleanedText=re.sub('@\S+',' ',cleanedText)
  cleanedText=re.sub('#\S+',' ',cleanedText)
  cleanedText=re.sub('[%s]' % re.escape("""!@#$%^&*()_+-=[]{}|;:'\",.<>/?"""),' ',cleanedText)
  cleanedText=re.sub('\s+',' ',cleanedText)
  cleanedText = re.sub(r'[^\x00-\x7f]', ' ', cleanedText)
  return cleanedText

df['Resume']=df['Resume'].apply(lambda x:clean(x))
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
df['Category']=le.fit_transform(df['Category'])
from sklearn.feature_extraction.text import  TfidfVectorizer
tfidf=TfidfVectorizer(stop_words='english')
tfidf.fit(df.Resume)
input=tfidf.transform(df['Resume'])
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(input,df['Category'],test_size=0.2,random_state=42)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
clf=OneVsRestClassifier(KNeighborsClassifier())
clf.fit(x_train,y_train)
ypred=clf.predict(x_test)
print(ypred)
from sklearn.metrics import accuracy_score
accuracy_score(y_test,ypred)
from sklearn.metrics import confusion_matrix
cm=confusion_matrix(y_test,ypred)
plt.figure(figsize = (10, 7))
sns.heatmap(cm, annot = True, fmt = 'd')
import pickle
pickle.dump(tfidf,open('tfidf.pkl','wb'))
pickle.dump(clf, open('clf.pkl', 'wb'))
resume="""Skills

Design & Modeling Software: AutoCAD, Revit, Civil 3D, STAAD Pro, SketchUp, Bluebeam
Structural Engineering: Load Calculations, Structural Analysis, Foundation Design, Reinforced Concrete, Steel Structures, Earthquake Resilience
Project Management: Cost Estimation, Resource Planning, Project Scheduling (Microsoft Project, Primavera), Risk Assessment, Field Supervision
Surveying & GIS: Land Surveying, Topographic Mapping, ArcGIS, Drone Survey Analysis
Others: MS Excel (Advanced), Report Writing, Regulatory Compliance, Environmental Impact Analysis
Education Details

Bachelor’s in Civil Engineering
XYZ University, City, State
Role: Civil Engineer
Civil Engineer - XYZ Construction Solutions
City, State
January 2022 – Present

Company: XYZ Construction Solutions
Description: Provides structural and environmental engineering services for large-scale infrastructure projects.
Project Details
BRIDGE CONSTRUCTION PROJECT
Objective: Led the structural analysis and design of a 500-meter suspension bridge, ensuring stability and safety under variable loads.
Responsibilities:
Conducted load calculations and structural analysis to determine materials and reinforcement requirements.
Collaborated with architects, geotechnical engineers, and municipal authorities to align project specifications with regulatory standards.
Supervised on-site construction activities, performing quality control checks on concrete pouring, rebar placement, and formwork.
Tools & Technologies: AutoCAD, STAAD Pro, Civil 3D, Microsoft Project
RESIDENTIAL BUILDING DEVELOPMENT
Objective: Designed and managed the construction of a 30-unit residential complex, focusing on sustainable and earthquake-resistant structures.
Responsibilities:
Created detailed structural drawings and reinforcement plans using AutoCAD and Revit.
Performed seismic analysis to ensure compliance with earthquake resilience codes and standards.
Oversaw field teams for quality assurance and coordinated inspections with local authorities.
Tools & Technologies: Revit, AutoCAD, Civil 3D, MS Excel
ROADWAY IMPROVEMENT AND EXPANSION
Objective: Engineered the expansion of a 10-kilometer highway to reduce congestion and improve traffic flow.
Responsibilities:
Conducted site surveys and collaborated with the surveying team to produce topographic maps and evaluate drainage requirements.
Assisted in designing road layouts, grading plans, and drainage solutions to minimize environmental impact.
Prepared project cost estimates and schedules, coordinating with contractors to ensure adherence to timelines and budget.
Tools & Technologies: Civil 3D, ArcGIS, AutoCAD, Microsoft Project
Additional Technical Experience
Stormwater Management Design: Designed stormwater drainage systems for urban developments, including hydraulic modeling and floodplain analysis.
Environmental Impact Assessments: Assisted in conducting environmental assessments for infrastructure projects, analyzing soil and water samples to meet regulatory compliance.
Project Documentation: Prepared reports, permits, and risk assessments for submission to local and federal authorities."""
import pickle
clf = pickle.load(open('clf.pkl', 'rb'))
cleaned_resume = clean(myresume)
input_features = tfidf.transform([cleaned_resume])
prediction_id = clf.predict(input_features)[0]
category_mapping = {
    15: "Java Developer",
    23: "Testing",
    8: "DevOps Engineer",
    20: "Python Developer",
    24: "Web Designing",
    12: "HR",
    13: "Hadoop",
    3: "Blockchain",
    10: "ETL Developer",
    18: "Operations Manager",
    6: "Data Science",
    22: "Sales",
    16: "Mechanical Engineer",
    1: "Arts",
    7: "Database",
    11: "Electrical Engineering",
    14: "Health and fitness",
    19: "PMO",
    4: "Business Analyst",
    9: "DotNet Developer",
    2: "Automation Testing",
    17: "Network Security Engineer",
    21: "SAP Developer",
    5: "Civil Engineer",
    0: "Advocate",
}
cleaned_resume = clean(resume)
input_features = tfidf.transform([cleaned_resume])
prediction_id = clf.predict(input_features)[0]
category_name = category_mapping.get(prediction_id, "Unknown")
print("Predicted Category:", category_name)