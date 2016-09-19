#ifndef ICE_MONGO_EXCEPTIONS
#define ICE_MONGO_EXCEPTIONS

module Base{
       exception BaseException{
           string message;
           int errorCode;
           string promot; 
       };
};

#endif