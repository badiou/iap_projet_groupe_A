
import os
from flask import Flask, abort, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv #permet d'importer les variables d'environnement
load_dotenv()

app=Flask(__name__)
###############################################################
# configuration de la base de données et de l'app Flask
#
###############################################################
#motdepasse=quote_plus('B@diou2015')
#hostname=os.getenv('host')

#app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:{}@{}:5432/api_db".format(motdepasse,hostname)
app.config['SQLALCHEMY_DATABASE_URI']='postgres://pjvhicwbuhdzrz:cfc6cec73d4c5902affb3989583d2fda75ee40661c699ef29ed029834c666ba5@ec2-34-206-148-196.compute-1.amazonaws.com:5432/d4u7tqk7f8ik5v'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
###############################################################
#
# declaration de la classe constructeur et methodes
###############################################################
class Etudiant(db.Model):
    __tablename__='etudiants'
    id=db.Column(db.Integer,primary_key=True)
    nom=db.Column(db.String(100),nullable=False)
    adresse=db.Column(db.String(200),nullable=True)
    email=db.Column(db.String(200),unique=True)
    
    def __init__(self, nom, adresse, email):
        self.nom = nom
        self.adresse = adresse
        self.email = email

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
        'id': self.id,
        'nom': self.nom,
        'adresse': self.adresse,
        'email': self.email,
        }
    
db.create_all()
###############################################################
#
#  Liste des tous les etudiants
###############################################################
@app.route('/etudiants',methods=['GET'])
def get_all_students():
    etudiants=Etudiant.query.all()
    formated_students=[ etudiant.format() for etudiant in etudiants]
    return jsonify(
    {
        'success':True,
        'etudiants':formated_students,
        'total':len(Etudiant.query.all())
    })
###############################################################
#
# Ajouter un nouvel etudiant
###############################################################
@app.route('/etudiants',methods=['POST'])
def add_student():
    body=request.get_json()
    new_nom=body.get('nom',None)
    new_email=body.get('email',None)
    new_adresse=body.get('adresse',None)
    if new_nom is None or new_email is None:
        abort(400)
    else:
        etudiant=Etudiant(nom=new_nom,email=new_email,adresse=new_adresse)
        etudiant.insert()
        etudiants=Etudiant.query.all()
        etudiants_formated=[etudiant.format() for etudiant in etudiants]
        
        return jsonify({
            'created_id':etudiant.id,
            'success':True,
            'total':Etudiant.query.count(),
            'etudiants':etudiants_formated 
        })
###############################################################
#Selectionner un etudiant
#
###############################################################
@app.route('/etudiants/<int:id>',methods=['GET'])
def get_one_student(id):
    
    etudiant=Etudiant.query.get(id)
#etudiant=Etudiant.query.filter(Etudiant.id==id).first()
    if etudiant is None:
        abort(404)
    else:
        return jsonify({
            "sucess":True,
            "selected_id":id,
            "selected_student":etudiant.format()
        })
   
###############################################################
#
#Supprimer un etudiant
###############################################################
@app.route('/etudiants/<int:id>',methods=['DELETE'])
def delete_student(id):
    etudiant=Etudiant.query.get(id)
    if etudiant is None:
        abort(404)
    else:
        etudiant.delete()
        return jsonify({
            "deleted_id":id,
            "success":True,
            "total":Etudiant.query.count(),
            "deleted_student":etudiant.format()
        })
###############################################################
#
#Modifier un étudiant
###############################################################        
@app.route('/etudiants/<int:id>',methods=['PATCH'])
def update_student(id):
    #get data from json
    body=request.get_json()
    #get student from database
    etudiant=Etudiant.query.get(id)
    #populate student object
    etudiant.nom=body.get('nom',None)
    etudiant.adresse=body.get('adresse',None)
    etudiant.email=body.get('email',None)
    
    if etudiant.nom is None or etudiant.adresse is None or etudiant.email is None:
        abort(400)
    else: 
        etudiant.update()
        return jsonify({
            "success":True,
            "updated_id_student":id,
            "new_student":etudiant.format()
        })
###############################################################
#
#   capturer la liste des erreurs
###############################################################              
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404
    
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "----Internal server error----"
        }), 500
       
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request"
        }), 400
    
if __name__=='main':
    app.run(debug=True)
