#ifndef ICE_MONGO_BASE

#define ICE_MONGO_BASE
#include "exceptions.ice"

module Base{
       class TBaseEntity{
             long id;
             bool isValid=true;
             long updateTime;
             long createTime;
       };

       sequence<TBaseEntity> EntityList;
       
       class QueryResult{
             int total;
             int offset;
             EntityList result;
       };

       interface BaseService{
             QueryResult query(TBaseEntity T, string queryString) throws BaseException;
             QueryResult batchUpdate(TBaseEntity T, string filterString, string updateString) throws BaseException;
             TBaseEntity getById(TBaseEntity T, long id) throws BaseException;
             TBaseEntity getOneByFilter(TBaseEntity T, string filterString) throws BaseException;
             void deleteById(TBaseEntity T, long id) throws BaseException;
             TBaseEntity updateById(TBaseEntity entity) throws BaseException;
             TBaseEntity create(TBaseEntity entity) throws BaseException;
       };
};


#endif