# [swift泛型](https://github.com/miss-shiyi/miss-shiyi/issues/3)

#### 1. 泛型

> **泛型**：能够在我们定义的函数或方法中编写足够灵活、可重用性强的功能，并可以与任何类型的参数按照我们定义的要求进行工作。使用泛型，我们可以写出避免重复和以更抽象的方式明确表达自己意图的代码。 `泛型`是`Swift`中最强大的功能之一，在`Swift`的标准库里，很多都是使用泛型构建的。事实上，我们已经使用了很多基于泛型的库，只是自己没有察觉而已。例如，数组和字典类型就是泛型集合。我们既可以创建基于“Int”类型的数组，也可以创建基于“String”类型的数据。同样，我们可以为字典的值存储各种自己所需的类型值。

```swift
func chgangeTwodatas<T>(oneData: inout T , anotherData: inout T){
    print("转换之前的数据oneData=\(oneData),anotherData=\(anotherData)")
    let temp = oneData
    oneData = anotherData
    anotherData = temp
    
    print("交换之后的数据 oneData=\(oneData),anotherData=\(anotherData)")
    
}

var a3 = "mike"
var a4 = "jack"

chgangeTwodatas(oneData: &a3, anotherData: &a4)

```

> **_类型参数：指定命名一个占位符，使用一对尖括号括起来“<T>”，并且紧跟在函数后面，如“泛型转换函数<T>”。_**
