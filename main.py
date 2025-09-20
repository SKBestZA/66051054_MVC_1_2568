from model.model import  StudentRegistrationModel as Model
from controller.controller import StudentRegistrationController as Controller
from view.view import StudentRegistrationView as View
if __name__=="__main__":
   model=Model()
   controller=Controller(model=model)
   app=View(controller=controller)
   app.mainloop()
   print("run")