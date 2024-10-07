<?php
/*
 * OTOKU～オトナライフマガジン～申込フォーム 確認
 */
session_name('EHIME_CATV');
session_start();

// 日付取得
$dt_now_ym = date('Ym');//今月


// -------------------------------------------------------
//関数
// 確認画面テキスト表示
function confirm_displayNull($str) {
    if ($str === null) {
        return 'なし';
    }

    return $str;
}

function send_mail($data) {

    //申込日
    $date_now = date('Y年m月d日');
    $price = "OTOKU定期購読（年払い　3.025円）";
    if ($data['service'] == "利用なし") {
      $price = "OTOKU定期購読（半年払い　2.640円）";
    }

    //自社メール送信(複数ある場合は「,」で区切る)
    $to = 'eigyou@e-catv.ne.jp';
    //$to = 'r.tanaka@e-catv.ne.jp';
    //$to = 'h.kimura@e-catv.ne.jp';

    $cc = null;
    $bcc = null;

    //社内宛
    $from = "customer@e-catv.ne.jp";
    $subject = 'OTOKU～オトナライフマガジン～申込';

    $body =
    "お客様サービス部　ご担当者様\n\n"
    ."下記の内容にてOTOKU～オトナライフマガジン～申込がありました。\n"
    ."申込内容を確認し、手続きを進めてください。\n\n"
    ."■お申し込み日\n"
    . $date_now ."\n\n"
    ."■加入状況\n"
    . $data['service'] ."\n\n"
    ."■お客様ID\n"
    . confirm_displayNull($data['input_no']) ."\n\n"
    ."■氏名\n"
    . $data['name'] . "（" . $data['name_kana'] . "）". "様\n\n"
    ."■住所\n"
    . $data['address'] ."\n\n"
    ."■電話番号\n"
    . $data['phone_number'] . "\n\n"
    ."■メールアドレス\n"
    . $data['mail_address'] . "\n\n"
    ."■お申込み内容\n"
    . $price ."\n\n"
    ."■申込冊数\n"
    . $data['magazine_number'] . "冊\n\n"
    //."■配達開始希望月\n"
    //. $data['start_time'] . "\n\n"

    ."■同意事項\n"
    . implode(",", $data['agree']) . "\n\n";

    $body = mb_convert_encoding($body,"utf8");
    $subject = mb_convert_encoding($subject,"utf8");

    send_mail_me($from, $to, $subject, $body, $cc, $bcc);



    //自動返信メール
    $subject2 = '【愛媛ＣＡＴＶ】OTOKU～オトナライフマガジン～申込完了通知（自動送信メール）';

    $body2 = $data['name'] ."様\n\n"
    . "愛媛ＣＡＴＶです。お問い合わせありがとうございます。\n"
    . "下記の内容に関するお申し込みを受付いたしました。\n\n"
    . "■お申込内容\n"
    . "OTOKU～オトナライフマガジン～\n\n"
    . "■申込冊数\n"
    .  $data['magazine_number'] . "冊\n\n";
    //. "■配達開始希望月\n"
    //.  $data['start_time'] . "\n\n";

    $body2 .= "\n"
    ."----------\n"
    ."790-8509\n"
    ."愛媛県松山市大手町1-11-4\n"
    ."株式会社　愛媛ＣＡＴＶ\n"
    ."TEL：0120(93)1616(受付時間 平日　09:00～18:00)\n"
    ."※このメールに心あたりのない方は、お手数ですが本メールの送信元(customer@e-catv.ne.jp)までご連絡ください。\n\n";


    $body2 = mb_convert_encoding($body2,"utf8");
    $subject2 = mb_convert_encoding($subject2,"utf8");

    send_mail_customer($from, $data['mail_address'], $subject2, $body2);

}

/*お客さま自動返信用*/
/*送信元,送信先,件名,メッセージ*/
function send_mail_customer($fromaddr, $toaddr, $subject, $msg)
{

    $boundary = "----=_Boundary_" . uniqid(rand(1000,9999) . '_') . "_";

    $additional_headers = "From: {$fromaddr}\n";
    $additional_headers .= "MIME-Version: 1.0\n";
    $additional_headers .= "Content-Type: multipart/mixed; boundary=\"{$boundary}\"\n";
    $additional_headers .= "Content-Transfer-Encoding: 7bit";

    $msgbody = chunk_split(base64_encode($msg));

    $message = "--{$boundary}\n";
    $message .= "Content-Type: text/plain; charset=UTF-8\n";
    $message .= "Content-Transfer-Encoding: base64\n\n";
    $message .= "\n{$msgbody}\n\n";
    $message .= "--{$boundary}--\n";


    mb_send_mail($toaddr, $subject, $message, $additional_headers);


}

/*自社メール用(Ccとか付ける用)*/
/*送信元,送信先,件名,メッセージ, Cc宛先, Bcc宛先*/
function send_mail_me($fromaddr, $toaddr, $subject, $msg, $cc, $bcc)
{

    $boundary = "----=_Boundary_" . uniqid(rand(1000,9999) . '_') . "_";

    $additional_headers = "From: {$fromaddr}\n";
    if ($cc != null && $cc != "") {
        $additional_headers .= "Cc: {$cc}\n";
    }
    if ($bcc != null && $bcc != "") {
        $additional_headers .= "Bcc: {$bcc}\n";
    }
    $additional_headers .= "MIME-Version: 1.0\n";
    $additional_headers .= "Content-Type: multipart/mixed; boundary=\"{$boundary}\"\n";
    $additional_headers .= "Content-Transfer-Encoding: 7bit";

    $msgbody = chunk_split(base64_encode($msg));

    $message = "--{$boundary}\n";
    $message .= "Content-Type: text/plain; charset=UTF-8\n";
    $message .= "Content-Transfer-Encoding: base64\n\n";
    $message .= "\n{$msgbody}\n\n";
    $message .= "--{$boundary}--\n";


    mb_send_mail($toaddr, $subject, $message, $additional_headers);


}

// -------------------------------------------------------

$data = array();
$data['service'] = $_SESSION['service'];    //加入状況
$data['input_no'] = $_SESSION['input_no'];    //お客様ID
$data['name'] = $_SESSION['name'];    //お名前
$data['name_kana'] = $_SESSION['name_kana'];    //お名前(フリガナ)
$data['address'] = $_SESSION['address'];    //ご住所
$data['phone_number'] = $_SESSION['phone_number'];  //ご連絡先電話番号1
$data['mail_address'] = $_SESSION['mail_address'];    //メールアドレス
$data['magazine_number'] = $_SESSION['magazine_number'];    //申込冊数
//$data['start_time'] = $_SESSION['start_time'];    //配達開始希望月
$data['agree'] = $_SESSION['agree'];  //確認
$data['agree2'] = $_SESSION['agree2'];  //確認
$data['agree3'] = $_SESSION['agree3'];  //確認
$data['agree4'] = $_SESSION['agree4'];  //確認


// POSTであるとき（修正・確定ボタンを押した時）
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    //メール送信
    send_mail($data);

    // -- 完了ページへリダイレクト
    session_destroy();
    header('Location:' . "../complete/");
    exit();

}

//完了から戻るボタンor直リンク対策
if (!$_SESSION['s_flg']) {
    header('Location:' . "../");
    exit();
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<title>OTOKU～オトナライフマガジン～申込フォーム | 愛媛ＣＡＴＶ</title>
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})
  (window,document,'script','dataLayer','GTM-N4PDD7H');
</script>
<!-- End Google Tag Manager -->

<link rel="shortcut icon" type="image/x-icon" href="../favicon.ico"/>
<link rel="stylesheet" type="text/css" href="../common/files/libs/destyle.css"/>
<link rel="stylesheet" type="text/css" href="../files/css/form_common.css?10"/>
<script type="text/javascript" src="../common/files/libs/jquery-1.12.4.min.js"></script>
</head>
<body>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N4PDD7H" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->

  <header id="header">
    <h1 class="logo">
      <img src="../files/img/logo_2.png" width="118" height="21"/>
    </h1>
  </header>

  <div id="main">

    <form class="form-horizontal" method="post">

      <div class="form_header" style="">
        <h2>OTOKU～オトナライフマガジン～申込フォーム</h2>
      </div>
      <div class="form_header2">
        <h3>入力内容確認</h3>
      </div>

      <div class="form_table">

        <div class="form_group">
          <h3 class="group_label">加入状況</h3>

          <div id="" class="form_item">
            <label class="item_label">愛媛ＣＡＴＶサービスのご利用状況<span class="required">必須</span></label>
            <div>
              <?= $data['service'] ?>
            </div>
          </div>

        </div>

        <div class="form_group">
          <h3 class="group_label">お客さま情報</h3>

          <div id="" class="form_item" <?php if($data['service'] == "利用なし") echo 'style="display:none;"'; ?>>
            <label class="item_label">お客様ID(1～6桁)</label>
            <div>
              <?= confirm_displayNull($data['input_no']); ?>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label"><span <?php if($data['service'] == "利用なし") echo 'style="display:none;"'; ?>>愛媛ＣＡＴＶご契約者さま</span>氏名<span class="required">必須</span></label>
            <div>
              <?= $data['name'] ?>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label">フリガナ<span class="required">必須</span></label>
            <div>
              <?= $data['name_kana'] ?>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label"><span <?php if($data['service'] == "利用なし") echo 'style="display:none;"'; ?>>愛媛ＣＡＴＶご契約</span>住所<span class="required">必須</span></label>
            <div>
              <?= $data['address'] ?>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label">電話番号<span class="required">必須</span></label>
            <div>
              <?= $data['phone_number'] ?>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label">メールアドレス<span class="required">必須</span></label>
            <div>
              <?= $data['mail_address'] ?> <br>
            </div>
          </div>

          <div id="" class="form_item">
            <label class="item_label">申込冊数<span class="required">必須</span></label>
            <div>
              <?= $data['magazine_number'] . '冊' ?> <br>
            </div>
          </div>
<!--
          <div id="" class="form_item">
            <label class="item_label">配達開始希望月<span class="required">必須</span></label>
            <div>
              <?//= $data['start_time'] ?> <br>
            </div>
          </div>
-->
          <div id="" class="form_item">
            <label class="item_label">同意事項<span class="required">必須</span></label>
            <div class="form_table" style="padding:10px; margin-bottom:10px; margin-left:0%;">
              <ul <?php if($data['service'] == "利用なし") echo 'style="display:none;"'; ?>>
                <li>お申し込みは弊社サービスをご利用中で何らかの料金のお支払いがある方に限ります。</li>
                <li>愛媛ＣＡＴＶのサービスのご利用が無くなった場合は自動的に解約となります。</li>
                <?php if ($dt_now_ym <= 202403): ?>
                <li><font color="#FF3300">2024年3月31日までにお申し込み頂いた方には2ヶ月無料キャンペーンを行っておりますので2024年6月のご請求が初回請求となります。</font></li>
                <?php else: ?>
                <li><font color="#FF3300">申込みご初回は無料となりますので翌月からのご請求となります。</font></li>
                <?php endif; ?>
              </ul>

              <ul <?php if($data['service'] != "利用なし") echo 'style="display:none;"'; ?>>
                <li>定期購読コース　半年払い 2,640円（先払い）<br>
                    定期購読は自動更新となります。お取り止めの際は愛媛ＣＡＴＶまでご連絡ください。<br>
                    お支払い方法は半年払いのみとさせていただいております。
                </li>
                <li>本フォームは愛媛ＣＡＴＶサービスのご利用がない方に限ります。</li>
                <li>お支払い方法については口座振替・クレジットが選択できます。</li>
                <li>本日から数営業日以内に口座・クレジットカード情報の記入用紙を送付いたしますのでご返送をお願いいたします。ご返送のない場合、督促状を送付させていただきます。あらかじめご了承ください。</li>
                <li>愛媛ＣＡＴＶサービスに加入された場合、月額275円の特別価格に変更となります。</li>
                <?php if ($dt_now_ym <= 202403): ?>
                <li><font color="#FF3300">2024年3月31日までにお申し込み頂いた方には2ヶ月無料キャンペーンを行っておりますので2024年6月のご請求が初回請求となります。</font></li>
                <?php else: ?>
                <li><font color="#FF3300">申込みご初回は無料となりますので翌月からのご請求となります。</font></li>
                <?php endif; ?>
              </ul>
            </div>
            <div>
              <?= implode(",", $data['agree']) ?>
            </div>
          </div>

        </div>

      </div>


      <div class="form_button">
        <input type="button" class="button large_button white_button" value="戻る" onclick="location.href='../'; return true" />
        <button class="button large_button blue_button">送信</button>
      </div>

    </form>

  </div>

  <footer id="footer">
    <div id="footer_inner">
      <p style="text-align:right;">Copyright &copy; EHIME CATV, Inc.</p>
    </div>
  </footer>

  <script type="text/javascript" src="../files/js/common.js?014"></script>
</body>
</html>