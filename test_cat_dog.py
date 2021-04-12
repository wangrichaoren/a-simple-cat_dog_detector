import paddlex as pdx
import cv2 as cv
import time
import os

if __name__ == '__main__':
    imgs_path = 'C:\\Users\\12168\\Desktop\\my_data\\JPEGImages'
    imgs_name = os.listdir(imgs_path)
    predicter_start_time = time.time()
    predictor = pdx.deploy.Predictor('./inference_model_cat_dog')
    print('开启检测器成功，耗时 {} s'.format(time.time() - predicter_start_time))
    # 创建窗口
    # cv.namedWindow('image',cv.WINDOW_NORMAL)

    for img_name in imgs_name:
        start = time.time()
        img_file_path = os.path.join(imgs_path, img_name)
        # print(img_file_path)
        # [{'category_id': 1, 'bbox': [541.8292846679688, 1937.986572265625, 1089.2105102539062, 1291.7890625], 'score': 0.9997640252113342, 'category': 'cat'}]...[]
        img = cv.imread(img_file_path)
        result = predictor.predict(img)

        for single in result:
            bbox = single['bbox']
            score = single['score']
            category = single['category']
            if score > 0.7:
                cv.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])),
                             (0, 0, 255), 9)
                text = 'category: ' + str(category)
                cv.putText(img, text, (int(bbox[0]), int(bbox[1]) - 100), cv.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 8)

                end_time = time.time() - start
                cost_text = 'cost time: ' + str(end_time)
                cv.putText(img, cost_text, (0,100), cv.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0),
                           8)

                score_text = 'score: ' + str(score)
                cv.putText(img, score_text, (int(bbox[0]), int(bbox[1]) - 200), cv.FONT_HERSHEY_SIMPLEX, 4,
                           (255, 255, 0), 8)

            img = cv.resize(img, (800, 800))
            cv.imshow('image', img)

        cv.waitKey()
        cv.destroyAllWindows()
