# [swift和OC混编](https://github.com/miss-shiyi/miss-shiyi/issues/2)

#### 1. `swift`项目调用OC代码

1. `{targetName}-Bridging-Header.h`文件 ,把oc的头文件导进这个文件中




#### 2. oc项目调用`swift`代码

1. targetName-Swift.h 此文件系统生成，导入使用即可
2. 设置Defines Module 为Yes 
3. `swift`代码中要把类名加 `public`
4.  方法和属性 要加 `@objc ` `public`
```swift
import UIKit

public class KKLabel: UIView {
    
 @objc public lazy var lab = UILabel()
 @objc public lazy var bt = UIButton()

  @objc public func initText(withFrame: CGRect, text: String) {
    
      lab = UILabel.init(frame: CGRect.init(x: 15, y: UIApplication.shared.statusBarFrame.size.height + 60, width: UIScreen.main.bounds.size.width - 30, height: 60));
      lab.text = text
      lab.font = .systemFont(ofSize: 12)
      lab.textColor = .black
      lab.numberOfLines = 0
      self.addSubview(lab)
      
      bt = UIButton.init(type: .custom)
      bt.setTitle("woshiBT", for: .normal)
      bt.setTitleColor(.blue, for: .normal)
      bt.addTarget(self, action: #selector(buuton), for: .touchUpInside)
      bt.titleLabel?.font = .systemFont(ofSize: 16)
      bt.backgroundColor = .gray
      bt.frame = CGRect.init(x: 60, y: lab.frame.origin.y + 120, width: UIScreen.main.bounds.size.width-120, height: 50)
      self.addSubview(bt)
      
    }
    
    @objc func buuton(){
        
        print("=========")
    }
    /*
    // Only override draw() if you perform custom drawing.
    // An empty implementation adversely affects performance during animation.
    override func draw(_ rect: CGRect) {
        // Drawing code
    }
    */

}

```