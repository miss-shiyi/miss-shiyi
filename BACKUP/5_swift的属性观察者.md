# [swift的属性观察者](https://github.com/miss-shiyi/miss-shiyi/issues/5)

##### 1. 属性观察者
 + `willSet `会在该值被存储之前被调用。 
+ `didSet `会在一个新值被存储后被调用。 
+  如果你实现了一个 willSet 观察者，新的属性值会以常量形式参数传递。你可以在你的 `willSet `实现中为这个参数定义名字。如果你没有为它命名，那么它会使用默认的名字`newValue` 。
 + 如果你实现了一个` didSet`观察者，一个包含旧属性值的常量形式参数将会被传递。你可以为它命名，也可以使用默认的形式参数名 `oldValue `。如果你在属性自己的 `didSet` 观察者里给自己赋值，你赋值的新值就会取代刚刚设置的值。

```swift

class StepCounter {
    
    var totalSteps: Int = 0 {
        willSet {
            print("will set total to a new value \(newValue)")
        }
        didSet {
            if (totalSteps > oldValue){
                print("add \(totalSteps - oldValue) steps")
            }else{
                print("退步了\(oldValue - totalSteps)")
            }
        }
    }
}

let stes = StepCounter()
stes.totalSteps = 200
stes.totalSteps = 360
stes.totalSteps = 896

```

> 全局和局部变量 • 观察属性的能力同样对全局变量和局部变量有效。全局变量是定义在任何函数、方法、闭包
或者类型环境之外的变量。局部变量是定义在函数、方法或者闭包环境之中的变量

```swift
var count: Int = 0 {
    willSet{
        print("about to use \(newValue)")
    }
    didSet {
        if count > oldValue {
            print("add\(count - oldValue)")
        }
    }
}

count = 10
if count == 10 {
    
    print("ten")
    
}
```
