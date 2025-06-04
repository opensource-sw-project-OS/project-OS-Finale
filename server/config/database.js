require('dotenv').config(); // 이 줄을 추가하세요!

const mysql = require('mysql2/promise');

// MySQL 연결 설정
const createPool = () => {
  try {
    return mysql.createPool({
      host: process.env.DB_HOST || '127.0.0.1',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '.',
      database: process.env.DB_NAME || 'receipt_app',
      waitForConnections: true,
      connectionLimit: 5,
      queueLimit: 0,
      timezone: '+09:00',
      dateStrings: true,
    //   ssl: {
    //     rejectUnauthorized: false
    //   }
    });
  } catch (error) {
    console.error('풀 생성 오류:', error);
    return null;
  }
};

// 데이터베이스 연결을 선택적으로 만듭니다
let pool = null;

try {
  pool = createPool();
  console.log('데이터베이스 연결 풀이 생성되었습니다.');
  require('dotenv').config();
  console.log('DB_USER from env:', process.env.DB_USER);
  console.log('DB_PASSWORD from env:', process.env.DB_PASSWORD); // 여기에 실제 비밀번호가 출력되어야 합니다. (주의: 실제 운영 환경에서는 로그에 비밀번호를 남기지 마세요)

  const mysql = require('mysql2/promise');
  
} catch (err) {
  console.error('데이터베이스 연결 풀 생성 실패:', err);
}

// 쿼리 래퍼 함수: 데이터베이스 오류 발생 시 빈 결과 반환
const safeQuery = async (query, params = []) => {
  try {
    if (!pool) {
      console.warn('데이터베이스 연결이 없습니다. 기본값을 반환합니다.');
      return [[], null];
    }
    return await pool.query(query, params);
  } catch (error) {
    console.error('쿼리 실행 오류:', error);
    return [[], null];
  }
};

// 연결 테스트
const testConnection = async () => {
  try {
    if (!pool) {
      console.warn('데이터베이스 연결이 없습니다. 서버는 제한된 기능으로 실행됩니다.');
      return;
    }
    
    const connection = await pool.getConnection();
    console.log('데이터베이스 연결 테스트 성공!');
    connection.release();
  } catch (err) {
    console.error('데이터베이스 연결 오류:', err);
    console.log('데이터베이스 연결 없이 제한된 기능으로 서버가 실행됩니다.');
  }
};

// 연결 테스트 실행
testConnection();

module.exports = {
  pool,
  query: safeQuery
};