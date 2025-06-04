const express = require('express');
const router = express.Router();
const db = require('../config/database');

/**
 * @swagger
 * tags:
 *   name: Receipts
 *   description: 영수증 관리 API
 */

/**
 * @swagger
 * components:
 *   schemas:
 *     Receipt:
 *       type: object
 *       required:
 *         - user_id
 *         - receipt_date
 *         - category
 *         - total_amount
 *       properties:
 *         receipt_id:
 *           type: integer
 *           description: 영수증 고유 ID
 *         user_id:
 *           type: integer
 *           description: 사용자 ID
 *         receipt_date:
 *           type: string
 *           format: date
 *           description: 영수증 날짜 (YYYY-MM-DD)
 *         category:
 *           type: string
 *           description: 영수증 카테고리
 *         total_amount:
 *           type: integer
 *           description: 총 금액
 *         emotion_type:
 *           type: string
 *           enum: [happy, sad, angry, anxious, neutral, null]
 *           description: 감정 유형
 *         emotion_description:
 *           type: string
 *           description: 감정 설명
 *       example:
 *         receipt_id: 1
 *         user_id: 1
 *         receipt_date: "2023-05-12"
 *         category: "식비"
 *         total_amount: 14500
 *         emotion_type: "happy"
 *         emotion_description: "오늘은 기분이 좋았습니다."
 */

/**
 * @swagger
 * /api/receipts/usage/month/{userId}:
 *   get:
 *     summary: 특정 사용자의 이번 달 지출 총합 조회
 *     tags: [Receipts]
 *     parameters:
 *       - in: path
 *         name: userId
 *         schema:
 *           type: integer
 *         required: true
 *         description: 조회할 사용자 ID
 *     responses:
 *       200:
 *         description: 이번 달 지출 총합을 반환
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 total_used:
 *                   type: integer
 *                   description: 이번 달 사용한 금액 총합
 *       400:
 *         description: 유효하지 않은 사용자 ID
 *       500:
 *         description: 서버 오류
 */
router.get('/usage/month/:userId', async (req, res) => {
  const userId = req.params.userId;

  if (!userId || isNaN(userId)) {
    return res.status(400).json({ message: '유효하지 않은 사용자 ID입니다.' });
  }

  try {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
    const nextMonth = month === 12 ? 1 : month + 1;
    const nextYear = month === 12 ? year + 1 : year;
    const endDate = `${nextYear}-${String(nextMonth).padStart(2, '0')}-01`;

    console.log('userId:', userId, 'startDate:', startDate, 'endDate:', endDate);

    const [rows] = await db.query(
      `SELECT IFNULL(SUM(total_amount), 0) AS total_used
       FROM receipt
       WHERE user_id = ? AND receipt_date >= ? AND receipt_date < ?`,
      [userId, startDate, endDate]
    );

    console.log('query result:', rows);

    res.status(200).json({ total_used: rows[0].total_used });
  } catch (error) {
    console.error('이번 달 지출 총합 조회 오류:', error);
    res.status(500).json({ total_used: 0 });
  }
});

module.exports = router;


// 기간 내 사용 금액 및 감정별 데이터를 가져오는 API
router.get('/usage/range', async (req, res) => {
  const userId = req.query.userId;
  const startDate = req.query.start; // YYYY-MM-DD
  const endDate = req.query.end;     // YYYY-MM-DD

  if (!userId || !startDate || !endDate) {
    return res.status(400).json({ message: 'userId, start, end 쿼리 파라미터가 필요합니다.' });
  }

  try {
    // 기간 내 해당 사용자 영수증 데이터 조회
    const [rows] = await db.query(
      `SELECT receipt_date AS date, emotion_type AS emotion, SUM(total_amount) AS amount
       FROM receipt
       WHERE user_id = ? AND receipt_date BETWEEN ? AND ?
       GROUP BY receipt_date, emotion_type
       ORDER BY receipt_date ASC`,
      [userId, startDate, endDate]
    );

    // 예: [{ date: '2025-06-01', emotion: '기쁨', amount: 14000 }, ...]
    res.json(rows);
  } catch (error) {
    console.error('기간 내 영수증 조회 오류:', error);
    res.status(500).json({ message: '서버 오류가 발생했습니다.' });
  }
});

module.exports = router;