from frema import Frema

f = Frema('varsayilan')
f.say("[ciddi] Geçen hafta sonu arkadaşlarımla birlikte şehrin dışına doğru uzun bir yürüyüşe çıktık. Hava beklediğimizden çok daha soğuktu ama manzara bütün yorgunluğumuzu unutturacak kadar güzeldi. Yolun yarısında küçük bir kahvaltıcıda mola verdik, sıcak çay içtik ve biraz dinlendikten sonra tekrar yola koyulduk. Akşam eve döndüğümüzde hepimiz çok yorgunduk ama bir sonraki hafta için yeni bir plan yapmaya başlamıştık bile.", path='test/1_anlatim.wav')
print('1 ok')

f.say("[haber] Az önce ajanslara düşen bilgilere göre, ülke genelinde etkili olacak kar yağışının üç gün süreceği tahmin ediliyor. Meteoroloji uzmanları, özellikle yüksek kesimlerde buzlanma ve ulaşımda aksamalar yaşanabileceği konusunda uyarıda bulundu. Yetkililer, sürücülerin zorunlu olmadıkça trafiğe çıkmamasını ve okulların tatil edilme ihtimaline karşı velilerin duyuruları takip etmesini istedi.", path='test/2_haber.wav')
print('2 ok')

f.say("[heyecanlı] Şu an canlı yayınımızda perde arkasından izlediğimiz ekip, sahneye çıkmadan önce son hazırlıklarını tamamlıyor. Işıklar yavaş yavaş kararıyor, seyircilerde büyük bir heyecan dalgası var. Sahne arkasında çalışan teknisyenler tüm ekipmanları tek tek kontrol ediyor. Performansın ilk bölümünde sürpriz bir misafir sanatçı da yer alacak, bu detayı kimse bilmiyordu. Yaklaşık beş dakika sonra ışıklar yanacak ve program başlayacak.", path='test/3_canli.wav')
print('3 ok')

fk = Frema('kadin')
fk.say("[romantik] Gecenin sessizliğinde odanın penceresinden içeri vuran ay ışığı, eski ahşap zemini gümüş bir yola dönüştürmüştü. Kimse konuşmuyordu. Sadece uzaktan gelen hafif bir rüzgar sesi ve camın ardındaki ağacın titreşimi vardı. Tüm yıldızlar sanki sadece o an için parlamaya başlamıştı. Sanki dünya biraz durmuştu da herkes kendi düşüncelerinin içine geri dönmüştü.", path='test/4_kadin.wav')
print('4 ok')

ff = Frema('derin_erkek')
ff.say("[ciddi] Bu görevin başarıyla tamamlanması her şeyden önce disiplin gerektirir. Hiçbir adım aceleyle atılmayacak, her karar titizlikle alınacaktır. Ekibin her bir üyesi sorumluluklarının farkındadır ve hata payı sıfıra yakındır. Riskler önceden hesaplandı, plan B ve C hazır. Hazırsanız başlayalım.", path='test/5_derin.wav')
print('5 ok')
